from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

API_LINK = 'https://external.api/recipes'

class RecipeListView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            response = requests.get(API_LINK)
            response.raise_for_status()
            recipes = response.json()
            return Response(recipes, status=status.HTTP_200_OK)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# You should also include URL configuration for this view in urls.py
