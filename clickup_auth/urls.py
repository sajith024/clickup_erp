from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import google_auth_callback

urlpatterns = [
    path("auth", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/sign-in/google", google_auth_callback, name="google_sso"),
]
