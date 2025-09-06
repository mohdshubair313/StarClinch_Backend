from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django.shortcuts import get_object_or_404

from .models import Recipe, Rating
from .serializers import RecipeListSerializer, RecipeDetailSerializer, RatingSerializer
from .ratings import create_or_update_rating

# Custom permissions
class IsSeller(permissions.BasePermission):
    def has_permission(self, request):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'seller')

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'customer')

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('seller').all()
    throttle_classes = [ScopedRateThrottle]
    # dynamic serializer
    def get_serializer_class(self):
        if self.action in ('list',):
            return RecipeListSerializer
        return RecipeDetailSerializer

    def get_permissions(self):
        # create: only sellers
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsSeller()]
        # update/delete: owner only
        if self.action in ('update', 'partial_update', 'destroy'):
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        # rating action will set its own permissions
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # seller is request.user
        serializer.save(seller=self.request.user)

    # throttle scope dynamic mapping
    def get_throttles(self):
        if self.action == 'create':
            self.throttle_scope = 'recipes_create'
        return super().get_throttles()

    @action(detail=True, methods=['post'], url_path='rate', throttle_classes=[ScopedRateThrottle])
    def rate(self, request, pk=None):
        # only customers in requirement, restrict here
        if not request.user.is_authenticated:
            return Response({'detail':'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.role != 'customer':
            return Response({'detail':'Only customers can rate'}, status=status.HTTP_403_FORBIDDEN)

        recipe = self.get_object()
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score = serializer.validated_data['score']
        comment = serializer.validated_data.get('comment', '')
        rating = create_or_update_rating(request.user, recipe, score, comment)
        return Response(RatingSerializer(rating).data, status=status.HTTP_200_OK)
