from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follow, User

from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeSerializer, SubscriberSerializer,
                          TagSerializer)


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response({
                'errors': 'Вы не можете подписываться на самого себя'
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
                'errors': 'Вы не можете отписываться от самого себя'
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
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):

    model = Ingredient
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeViewSet(viewsets.ModelViewSet):

    model = Recipe
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.prefetch_related(
        'ingredients__ingredient'
    ).all().order_by('-pub_date')
    filterset_fields = ['author', ]


class SubscriptionsViewSet(UserViewSet):

    serializer_class = SubscriberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]    

    def get_queryset(self, *args, **kwargs):
        return User.objects.filter(subscribed__user=self.request.user)
