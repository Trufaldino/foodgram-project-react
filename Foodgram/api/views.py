from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.views import PermissionDenied

from recipes.models import *

from .serializers import *


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer