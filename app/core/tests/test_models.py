"""
Test models
"""
from decimal import Decimal
from unittest.mock import patch

from core import models
from django.contrib.auth import get_user_model
from django.test import TestCase


def create_user(**params):
    """Create and return a user"""
    default = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    default.update(params)
    user = get_user_model().objects.create_user(**default)
    return user


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating user with email successfully"""
        email = 'test@example.com'
        password = '123456789'
        user = create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is fully normalized for new users"""
        sample_emails = [
            ['test1@EXAMPle.COM', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@example.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = create_user(email=email, password='123456789')
            self.assertEqual(user.email, expected)

    def test_create_new_user_without_an_email(self):
        """Creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            create_user(email='', password='123456789')

    def test_create_superuser(self):
        """Test creation of superuser"""
        email = 'test@example.com'
        password = '123456789'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_success(self):
        """Test creating recipe was successful"""
        user = create_user(
            email='test@example.com',
            password='testpass123'
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='sample_recipe_name',
            time_minutes=5,
            price=Decimal('6.70'),
            description='sample_recipe_description',
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_recipe_tags_success(self):
        """Test creating recipe tags successfully"""
        user = create_user(email='test@example.com', password='testpass123')
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient_success(self):
        """Test creating an ingredient successfully"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='test_ingredient_name')

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
