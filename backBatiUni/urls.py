"""backBatiUni URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('data/', views.Data.as_view(), name='data'),
    path('createBase/', views.CreateBase.as_view(), name='createBase'),
    path('initialize/',  views.Initialize.as_view(), name='initialize'),
    path('payment/', views.Payment.as_view(), name='payment'),
    path('webhook/', views.Webhook.as_view(), name='webhook'),
    path('subscription/', views.Subscription.as_view(), name='subscription')
]
