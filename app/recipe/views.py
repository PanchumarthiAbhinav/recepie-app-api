"""Views for the recipe APIs"""

from core.models import Recipe
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import RecipeSerializer


# Create your views here.
class RecipeViewSets(viewsets.ModelViewSet):
    """view for manage recipe APIs."""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated users only"""
        return self.queryset.filter(user=self.request.user).order_by('-id')
