"""Test for recipe api endpoints"""

import os
import tempfile
from decimal import Decimal

from PIL import Image
from core.models import Recipe, Tag, Ingredient
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


def image_upload_url(recipe_id):
    """Create and return a recipe image url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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


def create_ingredient(user, **params):
    """Create and return a recipe ingredient """
    default = {
        'name': 'sample_ingredient_name'
    }
    default.update(params)
    ingredient = Ingredient.objects.create(user=user, **default)
    return ingredient



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
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_creating_recipe_with_new_tag(self):
        """Test creating a recipe with tags"""
        payload = {
            'title': 'sample_title',
            'time_minutes': 5,
            'price': Decimal('9.45'),
            'description': 'sample_recipe_description',
            'link': 'https://example.com/recipe.pdf',
            'tags': [
                {'name': 'Thai'},
                {'name': 'sushi'},
            ]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEquals(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            )
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating recipe with tags in db"""
        tag = Tag.objects.create(name='indinna meal', user=self.user)
        payload = {
            'title': 'Pongal',
            'time_minutes': 50,
            'price': Decimal('9.56'),
            'tags': [{'name': 'indinna meal'}, {'name': 'Breakfast'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            )
            self.assertTrue(exists)

    def test_create_tag_on_recipe_update(self):
        """Test creating a recipe tag on recipe update"""
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [
                {'name': 'Brunch'}
            ]
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Brunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tags(self):
        """Test assigning an existing tag on recipe update """
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        url = detail_url(recipe_id=recipe.id)
        payload = {'tags': [{'name': 'Lunch'}]}
        res = self.client.patch(url, payload, format='json')
        recipes = Recipe.objects.filter(user=self.user)
        recipe = recipes[0]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 1)
        self.assertNotIn(tag_breakfast, recipe.tags.all())
        self.assertIn(tag_lunch, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a specific recipe tags"""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with ingredients"""
        payload = {
            'title': 'Pongal',
            'time_minutes': 50,
            'price': Decimal('9.56'),
            'ingredients': [{'name': 'Cauliflower'}, {'name': 'Salt'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating recipie with an existing ingredient in the db """
        create_ingredient(user=self.user)
        payload = {
            'title': 'Pongal',
            'time_minutes': 50,
            'price': Decimal('9.56'),
            'ingredients': [{'name': 'sample_ingredient_name'}, {'name': 'lemon'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creation of ingredients on recipe update"""
        recipe = create_recipe(user=self.user)
        payload = {'ingredients': [{'name': 'Pepper'}]}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user)
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredients(self):
        """Test assigning an existing ingredient when updating a recipe."""
        recipe = create_recipe(user=self.user)
        ingredient1 = create_ingredient(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='Chili')
        payload = {'ingredients': [{'name': 'Chili'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a specific recipe ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload = {'ingredients': []}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    class ImageUploadTestApi(TestCase):
        """Test cas for image upload"""

        def setUp(self) -> None:
            self.client = APIClient()
            self.user = create_user()
            self.client.force_authenticate(user=self.user)
            self.recipe = create_recipe(user=self.user)

        def tearDown(self) -> None:
            self.recipe.image.delete()

        def test_upload_image_success(self):
            """Test uploading a recipe image"""
            url = image_upload_url(self.recipe.id)
            with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:  # tempfile is a helper python module for
                # creating temporary image files for image upload
                img = Image.new('RGB', (10, 10))  # creates the image file
                img.save(image_file, format='JPEG')  # saves it
                """once image is saved the pointer goes to the end of the image file so seek 
                takes the pointer back to the beginning of the image file to be uploaded"""
                image_file.seek(0)
                payload = {'image': image_file}  # adds it to the payload
                res = self.client.post(url, payload, format='multipart')

            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn('image', res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

        def test_upload_bad_image_request(self):
            """Test bad image upload request"""
            url = image_upload_url(recipe_id=self.recipe.id)
            payload = {'image': 'Noimageupload'}
            res = self.client.post(url, payload, format='multipart')

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
