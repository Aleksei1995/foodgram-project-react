from django.db.models import Sum
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from django_filters.rest_framework.backends import DjangoFilterBackend

from .filters import RecipeFilter, IngredientSearchFilter
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User
from .permissions import IsOwnerOrReadOnly
from .pagination import PageNumberPagination
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(UserViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response({
                'errors': 'Вы не можете подписаться на самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на данного пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({
                'errors': 'Вы не можете отписаться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            'errors': 'Вы уже отписались'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):

    model = Tag
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):

    model = Ingredient
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    queryset = Ingredient.objects.all()
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):

    model = Recipe
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = PageNumberPagination
    filterset_fields = ['is_favorited', 'is_in_shopping_cart']

    # def get_queryset(self):
    #    queryset = Recipe.objects.all()
    #    is_favorited = self.request.query_params.get('is_favorited')
    #    is_in_shopping_cart = self.request.query_params.get(
    #        'is_in_shopping_cart')
    #    if is_favorited:
    #        queryset = queryset.filter(favorites__user=self.request.user)
    #    if is_in_shopping_cart:
    #        queryset = queryset.filter(shopping_cart__user=self.request.user)
    #    return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.add_object(Favorite, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_object(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.add_object(ShoppingCart, request.user, pk)
        elif request.method == 'DELETE':
            return self.delete_object(ShoppingCart, request.user, pk)
        return None

    def add_object(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список покупок'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShoppingCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_object(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт уже удален'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def set_download_shopping_cart(self, request):
        recipes_in_shopping_cart = ShoppingCart.objects.filter(
            user=request.user
        ).values_list('recipe__id')
        user = request.user
        ingredients = (
            IngredientInRecipe.objects.select_related('ingredient')
            .filter(recipe__id__in=recipes_in_shopping_cart)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total=Sum('amount'))
        )
        filename = '{}_list.txt'.format(user.username)
        products = []
        for ingredient in ingredients:
            products.append(
                '{} ({}) - {}'.format(
                    ingredient["ingredient__name"],
                    ingredient["ingredient__measurement_unit"],
                    ingredient["total"]))
        content = 'Продукт (единицы) - количество \n \n' + '\n'.join(products)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
