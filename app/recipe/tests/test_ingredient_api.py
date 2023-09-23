"""Tests for the ingredient API endpoints"""

from core.models import Ingredient
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
    default.update(**params)
    ingredient = Ingredient.objects.create(user=user, **default)
    return ingredient


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
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)
