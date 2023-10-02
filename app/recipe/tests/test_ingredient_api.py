"""Tests for the ingredient API endpoints"""

from decimal import Decimal

from core.models import Ingredient, Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import IngredientsSerializer
from rest_framework import status
from rest_framework.test import APIClient

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(**params):
    """Create and return a user"""
    default = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    default.update(params)
    user = get_user_model().objects.create_user(**default)
    return user


def create_ingredient(user, **params):
    """Create and return a recipe ingredient """
    default = {
        'name': 'sample_ingredient_name'
    }
    default.update(params)
    ingredient = Ingredient.objects.create(user=user, **default)
    return ingredient


def detail_url(ingredient_id):
    """Create and return an ingredient detail url"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Testing unauthenticated user request"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Testing authentication for API request"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Testing authenticated API requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Testing retrieving a list of ingredients"""
        create_ingredient(user=self.user)
        create_ingredient(user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-id')
        serializer = IngredientsSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_list_limited_to_user(self):
        """ Double-checking listing of ingredients is limited to only authenticated user"""
        other_user = create_user(email='test2@example.com', password='testoadfss123')
        create_ingredient(user=other_user)
        create_ingredient(user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredient = Ingredient.objects.filter(user=self.user)
        serializer = IngredientsSerializer(ingredient, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        # print(res.data)
        self.assertEqual(len(res.data), 1)

    def test_update_ingredients(self):
        """Testing updating an ingredient"""
        ingredient = create_ingredient(user=self.user)
        payload = {
            'name': 'new_sample_ingredient__name'
        }
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient"""
        ingredient = create_ingredient(user=self.user)
        url = detail_url(ingredient_id=ingredient.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        user_ingredient = Ingredient.objects.filter(user=self.user)
        self.assertFalse(user_ingredient.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingedients to those assigned to recipes."""
        in1 = Ingredient.objects.create(user=self.user, name='Apples')
        in2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Crumble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientsSerializer(in1)
        s2 = IngredientsSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title='Herb Eggs',
            time_minutes=20,
            price=Decimal('4.00'),
            user=self.user,
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
