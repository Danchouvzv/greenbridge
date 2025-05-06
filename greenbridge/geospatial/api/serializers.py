"""
Serializers for the Geospatial API.
"""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from ..models import Location, ServiceArea, CollectionRoute, RoutePoint, DropoffPoint


class LocationSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for Location model."""
    
    class Meta:
        model = Location
        geo_field = 'point'
        fields = (
            'id', 'name', 'address', 'point', 'elevation', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ServiceAreaSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for ServiceArea model."""
    operator_name = serializers.ReadOnlyField(source='operator.get_full_name')
    
    class Meta:
        model = ServiceArea
        geo_field = 'polygon'
        fields = (
            'id', 'name', 'description', 'polygon', 'operator', 'operator_name', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class RoutePointSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for RoutePoint model."""
    
    class Meta:
        model = RoutePoint
        geo_field = 'point'
        fields = (
            'id', 'route', 'point', 'sequence', 'arrival_time', 'departure_time', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class CollectionRouteSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for CollectionRoute model."""
    operator_name = serializers.ReadOnlyField(source='operator.get_full_name')
    point_count = serializers.ReadOnlyField()
    points = RoutePointSerializer(many=True, read_only=True)
    
    class Meta:
        model = CollectionRoute
        geo_field = 'line'
        fields = (
            'id', 'name', 'description', 'line', 'operator', 'operator_name',
            'distance', 'estimated_duration', 'start_time', 'end_time',
            'is_optimized', 'point_count', 'points', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'point_count')


class CollectionRouteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a CollectionRoute with points."""
    points = RoutePointSerializer(many=True, required=False)
    
    class Meta:
        model = CollectionRoute
        fields = (
            'name', 'description', 'line', 'distance', 'estimated_duration',
            'start_time', 'end_time', 'is_optimized', 'points'
        )
    
    def create(self, validated_data):
        """Create a CollectionRoute with nested points."""
        points_data = validated_data.pop('points', [])
        route = CollectionRoute.objects.create(**validated_data)
        
        for point_data in points_data:
            RoutePoint.objects.create(route=route, **point_data)
            
        return route


class DropoffPointSerializer(GeoFeatureModelSerializer):
    """GeoJSON serializer for DropoffPoint model."""
    operator_name = serializers.ReadOnlyField(source='operator.get_full_name')
    accepted_materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DropoffPoint
        geo_field = 'point'
        fields = (
            'id', 'name', 'description', 'point', 'address', 'operator',
            'operator_name', 'operating_hours', 'contact_phone', 'contact_email',
            'website', 'is_active', 'accepted_materials', 'accepted_materials_count',
            'created_at'
        )
        read_only_fields = ('id', 'created_at', 'accepted_materials_count')
    
    def get_accepted_materials_count(self, obj):
        """Get count of accepted materials."""
        return obj.accepted_materials.count()


class NearbyPointsSerializer(serializers.Serializer):
    """Serializer for requesting nearby points."""
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    distance = serializers.FloatField(required=False, default=10.0, help_text="Distance in kilometers")
    limit = serializers.IntegerField(required=False, default=10) 