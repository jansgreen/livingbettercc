"""
URL configuration for livingBetterCC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings
from authentication.views import login_view, register_view


# Deprecated: in-person certifications aliases removed. ReportActivity is handled in 'home' app.


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('auth/',include(("authentication.urls", "authentication"), namespace="authentication")),
    # Compatibility aliases for tests and login_required default
    path('accounts/login/', login_view),
    path('authentication/register/', register_view),
    # Incluir URLs de la app de usuarios
    path('dashboard/', include('dashboard.urls')),  # Incluir URLs de la app de checkout
    path('shop/', include(('shop.urls', 'shop'), namespace='shop')),
    path('cart/', include('cart.urls')),
    # In-person certifications routes removed; use 'home' ReportActivity views if needed.
    path('classroom/', include('classroom.urls')),
    path('google/auth/', include('googleauth.urls')),  # Maneja el login de Google
    path('auth/', include('social_django.urls', namespace='social')),  # Include URLs for social authentication
    path('gallery/', include('gallery.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('formbuilder/', include('formbuilder.urls')),
    path('payments/', include('payments.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
