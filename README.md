`README.md`

````markdown
# StarClinch Backend — Recipe Sharing & Rating Platform

##  Overview
This project implements a backend for a social media-like recipe platform using Django and Django REST Framework. It includes:

1. **Asynchronous image processing** — sellers upload images; Celery resizes and uploads them to Cloudinary.
2. **Authentication & Authorization** — via JWT (SimpleJWT).
3. **Ratings** — customers can rate recipes; average and count stored for fast retrieval.
4. **Daily Emails** — scheduled at 6 AM (Mon–Fri) via `django-celery-beat`.
5. **Weekly User Backup** — exports user data to local CSV file in `backups/` folder.
6. **Query optimization** — using `select_related`, aggregate fields, indexing, batch email sending.

---

##  Technologies Used

- Python, Django, Django REST Framework  
- Celery (with Redis) for background tasks  
- django-celery-beat for scheduling jobs  
- Cloudinary for image storage & CDN (via SDK)  
- PostgreSQL or SQLite (development)  
- Docker (optional) for containerization
-  UV package manager for fast cli command execution

---

##  Installation & Setup

### Clone & Install
```bash
git clone https://github.com/mohdshubair313/StarClinch_Backend.git
cd StarClinch_Backend
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
````

### Environment Variables

Create `.env` file in project root:

```env
SECRET_KEY=your-secret-key
DEBUG=True

# Cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Redis (Celery broker)
REDIS_URL=redis://localhost:6379/0

# Email (Console backend) — for development
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=from@example.com
```

Load with `django-environ` 

### Migrations

```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

### Start Services

In separate terminals:

```bash
# Terminal 1 — Django server
uv run manage.py runserver

# Terminal 2 — Redis (broker)
redis-server

# Terminal 3 — Celery worker
celery -A project worker -l info

# Terminal 4 — Celery beat (scheduler)
celery -A project beat -l info
```

---

## API Endpoints

| Endpoint                  | Method | Auth         | Description                          |
| ------------------------- | ------ | ------------ | ------------------------------------ |
| `/api/auth/register/`     | POST   | Public       | Register as customer or seller       |
| `/api/auth/token/`        | POST   | Public       | Get JWT token                        |
| `/api/recipes/`           | GET    | Public       | List recipes                         |
| `/api/recipes/`           | POST   | **Seller**   | Add a new recipe + image             |
| `/api/recipes/{id}/`      | GET    | Public       | Recipe detail with resized image URL |
| `/api/recipes/{id}/rate/` | POST   | **Customer** | Rate a recipe                        |

---

## Workflow Explanation

### Image Processing

1. Seller uploads recipe with original image via DRF.
2. `post_save` signal triggers `resize_and_upload_recipe_image` Celery task.
3. The task resizes the image, uploads to Cloudinary, and stores the CDN URL in `resized_image_url`.

### Daily Emails (6 AM Monday–Friday)

Scheduled via `django-celery-beat`. Sends personalized emails to users.

### Weekly User Data Backup

Scheduled via Celery beat. Exports user data to a CSV file in `backups/` directory. (S3 version available if needed.)

---

## Optimization Techniques

* `select_related('seller')` avoids extra DB hits on recipe listing.
* Stored aggregate fields (`avg_rating`, `rating_count`) for fast ratings display.
* Indexed fields used in queries (`created_at`, `seller`).
* Batch email processing avoids timeouts and rate limit issues.
* Celery handles all long-running tasks asynchronously for a responsive API.

---

## Running Tests (TBD)

Add tests for:

* API endpoints (recipe create, rate)
* Celery tasks (mock Cloudinary and backup CSV logic)
* Scheduling (beat tasks firing)

---

## Next Improvements

* Implement pagination and filtering (e.g., sort by popularity).
* Use direct S3/GCS/Cloud Run scheduling for production.
* Add full-text search or image caching.
* Add alerting/monitoring for failed tasks.

---

## File Structure

```
StarClinch_Backend/
├── project/                  # Django project
├── accounts/                 # Auth, users, email & backup tasks
├── recipes/                  # Recipe logic, image tasks
├── backups/                  # Local CSV backups
├── manage.py
└── README.md
``