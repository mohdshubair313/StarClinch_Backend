import cloudinary.uploader
from PIL import Image
import io
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
import datetime
from .models import Recipe

@shared_task
def resize_and_upload_recipe_image(recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        if not recipe.original_image:
            return "No image found"

        # Open file from Django FileField
        img = Image.open(recipe.original_image)
        img = img.convert("RGB")
        img.thumbnail((800, 800))

        # Save into memory buffer
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)

        # Upload to Cloudinary from buffer
        upload_result = cloudinary.uploader.upload(
            buffer,
            folder="recipes",
            resource_type="image",
            overwrite=True,
        )

        # Update model fields
        recipe.resized_image_url = upload_result.get("secure_url")
        recipe.cloudinary_public_id = upload_result.get("public_id")
        recipe.save(update_fields=["resized_image_url", "cloudinary_public_id"])

        return f"Uploaded to Cloudinary: {recipe.resized_image_url}"

    except Recipe.DoesNotExist:
        return "Recipe not found"
    except Exception as e:
        return f"Error: {str(e)}"


@shared_task
def send_daily_emails():
    """Send daily email to all users except weekends."""
    today = datetime.date.today()
    if today.weekday() in [5, 6]:  # Saturday=5, Sunday=6
        return "Skipped (weekend)"

    users = get_user_model().objects.all()
    for user in users:
        send_mail(
            subject="Daily Update",
            message=f"Hello {user.username}, here’s your daily update!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    return f"Sent emails to {users.count()} users"