"""Test for recipe api endpoints"""

from decimal import Decimal

from core.models import Recipe
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from rest_framework import status
from rest_framework.test import APIClient

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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


def create_user(**params):
    """Create and return a user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='tes@example.com', password='testoass123')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipies"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """ Double-checking listing of recipe is limited to only authenticated user"""
        other_user = create_user(email='test2@example.com', password='testoadfss123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_creating_recipe(self):
        """Test create recipe API endpoint"""
        payload = {
            'title': 'sample_recipe',
            'time_minutes': 30,
            'price': Decimal('50.9'),
            'description': 'sample_description'

        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Testing patch update"""
        original_link = 'https://examplle.com'
        recipe = create_recipe(user=self.user,
                               title='sample_title',
                               link=original_link
                               )

        url = detail_url(recipe_id=recipe.id)
        payload = {'title': 'New_recipe-title'}
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, res.data['title'])
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.link, original_link)

    def test_full_recipe_update(self):
        """Test updating all recipe fields"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)
        payload = {
            'title': 'new_sample_title',
            'time_minutes': 60,
            'price': Decimal('5.3'),
            'description': 'new_sample_description',
            'link': 'https://new_example.com'
        }

        res = self.client.put(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)  # this is the same thing with the code below
        # self.assertEqual(recipe.title, payload['title'])
        # self.assertEqual(recipe.description, payload['description'])
        # self.assertEqual(recipe.link, payload['link'])
        # self.assertEqual(recipe.price, payload['price'])
        # self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Testing changing recipe user results in error"""
        new_user = create_user(email='test@example.com', password='testpasswrod123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_recipe_success(self):
        """Testing deleting a recipe successfully"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete other users recipe data"""
        other_user = create_user(email='kosi@example.com', password='testpass123')
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe_id=recipe.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
