import django_filters as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(filters.FilterSet):

    author = filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    # is_favorited = filters.BooleanFilter(
    #    field_name='is_favorited',
    # )
    # is_in_shopping_cart = filters.BooleanFilter(
    #    field_name='is_in_shopping_cart',
    # )

    # def filter(self, queryset, name, value):
    #    if name == 'is_favorited' and value:
    #        queryset = queryset.filter(favorites__user=self.request.user)
    #    if name == 'is_in_shopping_cart' and value:
    #        queryset = queryset.filter(shopping_cart__user=self.request.user)
    #    return queryset

    def filter_queryset(self, queryset, view):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_favorited:
            queryset = queryset.filter(favorites__user=self.request.user)
        if is_in_shopping_cart:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_in_shopping_cart', 'is_favorited']


class IngredientSearchFilter(SearchFilter):

    search_param = 'name'
