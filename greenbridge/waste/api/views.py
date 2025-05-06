"""
API views for the Waste Management app.
"""
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from greenbridge.utils.permissions import IsOwner, IsRecycler, IsBrand
from greenbridge.utils.pagination import StandardResultsSetPagination
from ..models import (
    WasteCategory, Material, WasteCollection, CollectionItem,
    RecyclingFacility, RecyclingBatch
)
from .serializers import (
    WasteCategorySerializer, MaterialSerializer,
    WasteCollectionSerializer, WasteCollectionCreateSerializer,
    CollectionItemSerializer, RecyclingFacilitySerializer,
    RecyclingBatchSerializer, RecyclingBatchCreateSerializer,
    BatchInputSerializer, BatchOutputSerializer
)


class WasteCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for waste categories.
    """
    queryset = WasteCategory.objects.filter(is_deleted=False)
    serializer_class = WasteCategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recyclable', 'hazardous', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True)
    def subcategories(self, request, pk=None):
        """List all subcategories for a specific category."""
        category = self.get_object()
        subcategories = WasteCategory.objects.filter(parent=category, is_deleted=False)
        page = self.paginate_queryset(subcategories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def materials(self, request, pk=None):
        """List all materials for a specific category."""
        category = self.get_object()
        materials = Material.objects.filter(category=category, is_deleted=False)
        page = self.paginate_queryset(materials)
        if page is not None:
            serializer = MaterialSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MaterialSerializer(materials, many=True)
        return Response(serializer.data)


class MaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint for materials.
    """
    queryset = Material.objects.filter(is_deleted=False)
    serializer_class = MaterialSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['recyclable', 'category']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at', 'value_per_kg']
    ordering = ['name']
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class WasteCollectionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for waste collections.
    """
    queryset = WasteCollection.objects.all()
    serializer_class = WasteCollectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'owner', 'recycler', 'brand']
    search_fields = ['location_name', 'address', 'custom_collection_code']
    ordering_fields = ['collection_date', 'created_at', 'status']
    ordering = ['-collection_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return WasteCollectionCreateSerializer
        return WasteCollectionSerializer
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Set owner to current user on create."""
        serializer.save(owner=self.request.user, created_by=self.request.user.email)
    
    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user.email)
    
    @action(detail=False)
    def my_collections(self, request):
        """List collections owned by current user."""
        collections = WasteCollection.objects.filter(owner=request.user)
        page = self.paginate_queryset(collections)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(collections, many=True)
        return Response(serializer.data)
    
    @action(detail=False, permission_classes=[IsRecycler])
    def recycler_collections(self, request):
        """List collections assigned to current recycler."""
        collections = WasteCollection.objects.filter(recycler=request.user)
        page = self.paginate_queryset(collections)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(collections, many=True)
        return Response(serializer.data)
    
    @action(detail=False, permission_classes=[IsBrand])
    def brand_collections(self, request):
        """List collections associated with current brand."""
        collections = WasteCollection.objects.filter(brand=request.user)
        page = self.paginate_queryset(collections)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(collections, many=True)
        return Response(serializer.data)


class CollectionItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for collection items.
    """
    queryset = CollectionItem.objects.all()
    serializer_class = CollectionItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection', 'material']
    search_fields = ['waste_code', 'notes']
    ordering_fields = ['created_at', 'weight']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class RecyclingFacilityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for recycling facilities.
    """
    queryset = RecyclingFacility.objects.filter(is_deleted=False)
    serializer_class = RecyclingFacilitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operator']
    search_fields = ['name', 'address', 'contact_email']
    ordering_fields = ['name', 'created_at', 'capacity']
    ordering = ['name']
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['create']:
            return [permissions.IsAuthenticated(), IsRecycler()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Set operator to current user on create."""
        serializer.save(operator=self.request.user)
    
    @action(detail=False, permission_classes=[IsRecycler])
    def my_facilities(self, request):
        """List facilities operated by current user."""
        facilities = RecyclingFacility.objects.filter(operator=request.user, is_deleted=False)
        page = self.paginate_queryset(facilities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(facilities, many=True)
        return Response(serializer.data)


class RecyclingBatchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for recycling batches.
    """
    queryset = RecyclingBatch.objects.all()
    serializer_class = RecyclingBatchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'facility']
    search_fields = ['batch_number', 'notes']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'total_input_weight']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecyclingBatchCreateSerializer
        return RecyclingBatchSerializer
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsRecycler()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Set created_by to current user on create."""
        serializer.save(created_by=self.request.user.email)
    
    def perform_update(self, serializer):
        """Set updated_by to current user on update."""
        serializer.save(updated_by=self.request.user.email) 