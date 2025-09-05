from django.db import transaction
from django.db.models import Avg, Count
from .models import Rating, Recipe

def create_or_update_rating(user, recipe, score, comment=None):
    with transaction.atomic():
        obj, created = Rating.objects.update_or_create(
            user=user, recipe=recipe,
            defaults={'score': score, 'comment': comment}
        )
        agg = Rating.objects.filter(recipe=recipe).aggregate(avg=Avg('score'), count=Count('id'))
        recipe.avg_rating = float(agg['avg'] or 0.0)
        recipe.rating_count = int(agg['count'] or 0)
        recipe.save(update_fields=['avg_rating','rating_count'])
    return obj
