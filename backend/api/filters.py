import django_filters as filters
from rest_framework.filters import SearchFilter

from recipes.models import Tag


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
    #    field_name='is_favorited'
    # )
    # is_in_shopping_cart = filters.BooleanFilter(
    #    field_name='is_in_shopping_cart'
    # )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited:
            queryset = queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientSearchFilter(SearchFilter):

    search_param = 'name'
