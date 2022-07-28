from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = User

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def get_is_subscribed(self, author):

        user = self.context['request'].user
        return (user.is_authenticated
                and user.subscriber.filter(author=author).exists())


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class AddIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True, source='ingredient.pk')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = AddIngredientSerializer(many=True,)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'name', 'text', 'cooking_time',
            'ingredients', 'image',
        )

    @staticmethod
    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe


class SubscriberSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
        )


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    author = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    def validate(self, data):
        request = self.context.get('request')
        author = data['author']
        if request.user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data

    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [UniqueTogetherValidator(
            queryset=Follow.objects.all(),
            fields=('user', 'author')
        )]
