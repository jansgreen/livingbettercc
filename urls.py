from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('googleauth/', include('googleauth.urls')),
    # ...existing code...
]
