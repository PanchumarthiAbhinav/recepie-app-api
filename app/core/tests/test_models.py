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
        user = get_user_model().objects.create_user(
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
            user = get_user_model().objects.create_user(email, '123456789')
            self.assertEqual(user.email, expected)

    def test_new_user_without_an_email(self):
        """Creating a user without an email raises a Valueerror"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '123456789')

