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
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', method='filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', method='filter'
    )

    def filter(self, queryset, name, value):
        if name == 'is_favorited' and value:
            queryset = queryset.filter(favorites__user=self.request.user)
        if name == 'is_in_shopping_cart' and value:
            queryset = queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class IngredientSearchFilter(SearchFilter):

    search_param = 'name'
