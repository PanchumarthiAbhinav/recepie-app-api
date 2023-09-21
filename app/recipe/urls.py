"""Endpoints for recipe API"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSets

router = DefaultRouter()
router.register('recipes', viewset=RecipeViewSets)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
