"""Test for recipe api endpoints"""

from decimal import Decimal

from core.models import Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPE_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """Create and return recipes"""
    defaults = {
        'title': 'sample_title',
        'time_minutes': 5,
        'price': Decimal('9.45'),
        'description': 'sample_recipe_description',
        'link': 'https://example.com/recipe.pdf'
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Testing unauthenticated API requests"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication required for API request"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Testing authorized API requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipies"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all.order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """ Double-checking listing of recipe is limited to only authenticated user"""
        other_user = get_user_model().objects.create_user(
            'other_user@example.com'
            'other_userpass123'
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
