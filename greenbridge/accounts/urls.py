"""
URL patterns for the Accounts app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    UserViewSet, UserLoginView, UserProfileView,
    PasswordResetRequestView, PasswordResetConfirmView
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)

app_name = 'accounts'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
    path('api/login/', UserLoginView.as_view(), name='login'),
    path('api/profile/', UserProfileView.as_view(), name='profile'),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
] 