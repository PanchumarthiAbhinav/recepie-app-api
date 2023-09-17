"""
Test models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating user with email successfully"""
        email = 'test@example.com'
        password = '123456789'
        user = get_user_model().objects.create(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.checkpassword(password))
