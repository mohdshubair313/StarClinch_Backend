# project/urls.py
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  
    path('api/auth/', include('users.urls')),   
    path('api/recipes/', include('recipes.urls')),
]
