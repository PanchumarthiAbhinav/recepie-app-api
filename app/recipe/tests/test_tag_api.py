"""Tests for recipe tag API endpoints"""

from core.models import Tag
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from recipe.serializers import TagSerializer
from rest_framework import status
from rest_framework.test import APIClient

TAGS_URL = reverse('recipe:tag-list')


def create_user(**params):
    """Helper function for creating and returning users"""
    return get_user_model().objects.create_user(**params)


def create_tag(user, **params):
    """Helper function for creating and returning tags"""
    defaults = {
        'name': 'sample_tag_name',
    }
    defaults.update(params)
    tag = Tag.objects.create(user=user, **defaults)
    return tag


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='test@example.com', password='testpass1234')
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags for auth user"""
        create_tag(user=self.user, name='tag1')
        create_tag(user=self.user, name='tag2')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tags_list_limited_to_auth_user(self):
        """ Double-checking listing of recipe is limited to only authenticated user"""
        other_user = create_user(email='kodi@exmple.com', password='testpass123')
        create_tag(user=other_user)
        create_tag(user=self.user)

        res = self.client.get(TAGS_URL)
        tag = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tag, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
