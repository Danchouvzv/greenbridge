"""
URL patterns for the Geospatial app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    LocationViewSet, ServiceAreaViewSet, CollectionRouteViewSet,
    RoutePointViewSet, DropoffPointViewSet
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'service-areas', ServiceAreaViewSet)
router.register(r'routes', CollectionRouteViewSet)
router.register(r'route-points', RoutePointViewSet)
router.register(r'dropoff-points', DropoffPointViewSet)

app_name = 'geospatial'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
] 