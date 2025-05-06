"""
URL Configuration for the GreenBridge project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Create URL patterns
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API documentation
    path('openapi/', get_schema_view(
        title="GreenBridge API",
        description="API for GreenBridge, a sustainable waste management platform",
        version="1.0.0"
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    
    # JWT auth endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # App URLs
    path('accounts/', include('greenbridge.accounts.urls')),
    path('waste/', include('greenbridge.waste.urls')),
    path('geo/', include('greenbridge.geospatial.urls')),
    
    # Root URL
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

# Add debug toolbar URLs if in debug mode
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# WebSocket URL patterns (used by ASGI)
websocket_urlpatterns = [
    # TODO: Add WebSocket URL patterns for real-time features
] 