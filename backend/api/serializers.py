from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class UserSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('ingredient', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set',
        many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(favorites__user=user, id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(shopping_cart__user=user,
                                     id=obj.id).exists()

    def validate(self, data):
        ingredients = self.initial_data.pop('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингридиент для рецепта'})
        for ingredient_item in ingredients:
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError({
                    'ingredients': ('Убедитесь, что значение количества '
                                    'ингредиента больше 0')
                })
        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        ingredient_data = validated_data.pop('ingredientinrecipe_set')
        tags = self.initial_data.get('tags')
        new_recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            name=validated_data.pop('name'),
            text=validated_data.pop('text'),
            image=validated_data.pop('image'),
            cooking_time=validated_data.pop('cooking_time'),
        )
        new_recipe.save()
        new_recipe.tags.set(tags)
        for ingredients in ingredient_data:
            IngredientInRecipe.objects.create(
                recipe=new_recipe,
                **ingredients
            )
        return new_recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.pop('image', instance.image)
        instance.name = validated_data.pop('name', instance.name)
        instance.text = validated_data.pop('text', instance.text)
        instance.cooking_time = validated_data.pop(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags_data = self.initial_data.get('tags')
        instance.tags.set(tags_data)
        IngredientInRecipe.objects.filter(recipe=instance).all().delete()
        for ingredients in validated_data.pop('ingredients'):
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredients.get('ingredient'),
                amount=ingredients.get('amount'),
            )
        instance.save()
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        validators = [UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'author')
        )]

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShoppingCartSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
