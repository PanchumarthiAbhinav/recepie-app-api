"""Endpoints for recipe API"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSets, TagViewSets

router = DefaultRouter()
router.register('recipes', viewset=RecipeViewSets)
router.register('recipies/tags', viewset=TagViewSets)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
