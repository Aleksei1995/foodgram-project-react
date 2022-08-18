# Generated by Django 2.2.16 on 2022-08-15 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(null=True, related_name='recipes', through='recipes.IngredientInRecipe', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
    ]
