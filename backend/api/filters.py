import django_filters as filters

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
        method='get_is_in'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in'
    )

    def get_is_in(self, queryset, name, value):
        """
        Фильтрация рецептов по избранному и списку покупок.
        """
        user = self.request.user
        if user.is_authenticated:
            if value == '1':
                if name == 'is_favorited':
                    queryset = queryset.filter(favorites=user)
                if name == 'is_in_shopping_cart':
                    queryset = queryset.filter(shoppings=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
