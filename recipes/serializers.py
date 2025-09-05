from rest_framework import serializers
from .models import Recipe, Rating
from django.db.models import Avg

class RecipeListSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'resized_image_url', 'avg_rating', 'rating_count', 'seller_username', 'created_at']

class RecipeDetailSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'original_image', 'resized_image_url', 'avg_rating', 'rating_count', 'seller_username', 'created_at']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    score = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Rating
        fields = ['id','user','score','comment','created_at']
