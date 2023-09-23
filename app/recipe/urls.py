"""Endpoints for recipe API"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSets, TagViewSets, IngredientViewSets

router = DefaultRouter()
router.register('recipes', viewset=RecipeViewSets)
router.register('tags', viewset=TagViewSets)
router.register('ingredients', viewset=IngredientViewSets)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
