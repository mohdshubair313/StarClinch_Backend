# recipes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Recipe
from .tasks import resize_and_upload_recipe_image

@receiver(post_save, sender=Recipe)
def process_recipe_image(sender, instance, created, **kwargs):
    if created and instance.original_image:
        resize_and_upload_recipe_image.delay(instance.id)
