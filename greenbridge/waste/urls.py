"""
URL patterns for the Waste Management app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    WasteCategoryViewSet, MaterialViewSet, WasteCollectionViewSet,
    CollectionItemViewSet, RecyclingFacilityViewSet, RecyclingBatchViewSet
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'categories', WasteCategoryViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'collections', WasteCollectionViewSet)
router.register(r'collection-items', CollectionItemViewSet)
router.register(r'facilities', RecyclingFacilityViewSet)
router.register(r'batches', RecyclingBatchViewSet)

app_name = 'waste'

urlpatterns = [
    # API routes
    path('api/', include(router.urls)),
] 