from django.urls import path
from . import views

urlpatterns = [
    # ... your other url patterns
    path('recipes/', views.RecipeListView.as_view(), name='recipe-list'),
]