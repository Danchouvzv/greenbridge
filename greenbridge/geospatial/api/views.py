"""
API views for the Geospatial app.
"""
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import F

from greenbridge.utils.permissions import IsOwner, IsRecycler
from greenbridge.utils.pagination import StandardResultsSetPagination
from ..models import Location, ServiceArea, CollectionRoute, RoutePoint, DropoffPoint
from .serializers import (
    LocationSerializer, ServiceAreaSerializer, CollectionRouteSerializer,
    CollectionRouteCreateSerializer, RoutePointSerializer, DropoffPointSerializer,
    NearbyPointsSerializer
)


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for locations.
    """
    queryset = Location.objects.filter(is_deleted=False)
    serializer_class = LocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]


class ServiceAreaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for service areas.
    """
    queryset = ServiceArea.objects.filter(is_deleted=False)
    serializer_class = ServiceAreaSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operator']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
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
    def my_service_areas(self, request):
        """List service areas operated by current user."""
        areas = ServiceArea.objects.filter(operator=request.user, is_deleted=False)
        page = self.paginate_queryset(areas)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(areas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def contains_point(self, request):
        """Check if a point is contained in any service area."""
        serializer = NearbyPointsSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['latitude']
            lng = serializer.validated_data['longitude']
            point = Point(lng, lat, srid=4326)
            
            areas = ServiceArea.objects.filter(polygon__contains=point, is_deleted=False)
            page = self.paginate_queryset(areas)
            if page is not None:
                response_serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(response_serializer.data)
            response_serializer = self.get_serializer(areas, many=True)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionRouteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for collection routes.
    """
    queryset = CollectionRoute.objects.filter(is_deleted=False)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operator', 'is_optimized']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'start_time']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return CollectionRouteCreateSerializer
        return CollectionRouteSerializer
    
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
    def my_routes(self, request):
        """List routes operated by current user."""
        routes = CollectionRoute.objects.filter(operator=request.user, is_deleted=False)
        page = self.paginate_queryset(routes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(routes, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def points(self, request, pk=None):
        """List all points for a specific route."""
        route = self.get_object()
        points = RoutePoint.objects.filter(route=route).order_by('sequence')
        page = self.paginate_queryset(points)
        if page is not None:
            serializer = RoutePointSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RoutePointSerializer(points, many=True)
        return Response(serializer.data)


class RoutePointViewSet(viewsets.ModelViewSet):
    """
    API endpoint for route points.
    """
    queryset = RoutePoint.objects.all()
    serializer_class = RoutePointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['route']
    ordering_fields = ['sequence', 'created_at']
    ordering = ['sequence']
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsRecycler()]
        return [permissions.IsAuthenticated()]


class DropoffPointViewSet(viewsets.ModelViewSet):
    """
    API endpoint for dropoff points.
    """
    queryset = DropoffPoint.objects.filter(is_deleted=False, is_active=True)
    serializer_class = DropoffPointSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['operator', 'accepted_materials']
    search_fields = ['name', 'address', 'description']
    ordering_fields = ['name', 'created_at']
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
    
    @action(detail=False, methods=['post'])
    def nearby(self, request):
        """Find dropoff points near a given location."""
        serializer = NearbyPointsSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['latitude']
            lng = serializer.validated_data['longitude']
            distance = serializer.validated_data['distance']
            limit = serializer.validated_data['limit']
            
            user_location = Point(lng, lat, srid=4326)
            
            # Find dropoff points within the specified distance (km)
            points = DropoffPoint.objects.filter(
                is_deleted=False,
                is_active=True,
                point__distance_lte=(user_location, D(km=distance))
            ).annotate(
                distance=F('point__distance_value') * 100
            ).order_by('distance')[:limit]
            
            serializer = self.get_serializer(points, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 