"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from marketplace.views import (custom_login_view, register_view, confirm_email_view, resend_confirmation_view,)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('marketplace.urls')),
    
    #Аутентификация
    path('marketplace/login/', custom_login_view, name='login'),
    path('marketplace/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('marketplace/register/', register_view, name='register'),
    
    # Подтверждение email
    path('marketplace/confirm-email/<uidb64>/<token>/', 
         confirm_email_view, name='confirm_email'),
    path('marketplace/resend-confirmation/', 
         resend_confirmation_view, name='resend_confirmation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)