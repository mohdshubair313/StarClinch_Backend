from django.contrib import admin
from .models import Recipe, Rating

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'avg_rating', 'rating_count', 'created_at')
    search_fields = ('title', 'description', 'seller__username')
    list_filter = ('created_at', 'seller')
    readonly_fields = ('avg_rating', 'rating_count', 'created_at', 'updated_at')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'score', 'created_at')
    search_fields = ('user__username', 'recipe__title')
    list_filter = ('created_at', 'recipe')
    readonly_fields = ('created_at',)

admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Rating, RatingAdmin)
