import csv
import os
from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings
import datetime
import boto3
import io
from celery import shared_task


User = get_user_model()

@shared_task
def weekly_user_data_backup_local():
    """Export user data to local CSV weekly."""
    # Backup directory path (inside project BASE_DIR/backups)
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)  # create if not exists

    # Filename with today's date
    filename = f"users_{datetime.date.today()}.csv"
    filepath = os.path.join(backup_dir, filename)

    # Write CSV
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Username", "Email", "Date Joined"])

        for user in User.objects.all():
            writer.writerow([user.pk, user.username, user.email, user.date_joined])

    return f"User backup saved at {filepath}"


User = get_user_model()

@shared_task
def weekly_user_data_backup():
    """Export user data to S3 in CSV weekly."""
    # Create CSV in memory
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Username", "Email", "Date Joined"])

    for user in User.objects.all():
        writer.writerow([user.id, user.username, user.email, user.date_joined])

    buffer.seek(0)

    # Upload to S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    file_key = f"user_backups/users_{str(datetime.date.today())}.csv"

    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_key,
        Body=buffer.getvalue(),
        ContentType="text/csv"
    )

    return f"Uploaded backup to S3: {file_key}"
