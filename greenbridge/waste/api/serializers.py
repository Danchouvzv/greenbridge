"""
Serializers for the Waste Management API.
"""
from rest_framework import serializers
from ..models import (
    WasteCategory, Material, WasteCollection, CollectionItem,
    RecyclingFacility, RecyclingBatch, BatchInput, BatchOutput
)


class WasteCategorySerializer(serializers.ModelSerializer):
    """Serializer for WasteCategory model."""
    subcategories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WasteCategory
        fields = (
            'id', 'name', 'code', 'description', 'parent', 'recyclable',
            'hazardous', 'image', 'subcategories_count', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
    
    def get_subcategories_count(self, obj):
        """Get count of subcategories."""
        return obj.subcategories.count()


class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for Material model."""
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Material
        fields = (
            'id', 'name', 'code', 'description', 'category', 'category_name',
            'recyclable', 'value_per_kg', 'co2_offset_per_kg', 'image', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class CollectionItemSerializer(serializers.ModelSerializer):
    """Serializer for CollectionItem model."""
    material_name = serializers.ReadOnlyField(source='material.name')
    material_code = serializers.ReadOnlyField(source='material.code')
    total_value = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    co2_offset = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2
    )
    
    class Meta:
        model = CollectionItem
        fields = (
            'id', 'material', 'material_name', 'material_code', 'weight',
            'quantity', 'waste_code', 'notes', 'image', 'total_value',
            'co2_offset', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'total_value', 'co2_offset')


class WasteCollectionSerializer(serializers.ModelSerializer):
    """Serializer for WasteCollection model."""
    items = CollectionItemSerializer(many=True, read_only=True)
    owner_name = serializers.ReadOnlyField(source='owner.get_full_name')
    recycler_name = serializers.ReadOnlyField(source='recycler.get_full_name')
    brand_name = serializers.ReadOnlyField(source='brand.get_full_name')
    total_weight = serializers.ReadOnlyField()
    
    class Meta:
        model = WasteCollection
        fields = (
            'id', 'collection_date', 'status', 'location_name', 'address',
            'latitude', 'longitude', 'notes', 'owner', 'owner_name',
            'recycler', 'recycler_name', 'brand', 'brand_name',
            'custom_collection_code', 'items', 'total_weight',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'total_weight')


class WasteCollectionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a WasteCollection with items."""
    items = CollectionItemSerializer(many=True)
    
    class Meta:
        model = WasteCollection
        fields = (
            'collection_date', 'status', 'location_name', 'address',
            'latitude', 'longitude', 'notes', 'recycler', 'brand',
            'custom_collection_code', 'items'
        )
    
    def create(self, validated_data):
        """Create a WasteCollection with nested items."""
        items_data = validated_data.pop('items')
        collection = WasteCollection.objects.create(**validated_data)
        
        for item_data in items_data:
            CollectionItem.objects.create(collection=collection, **item_data)
            
        return collection


class RecyclingFacilitySerializer(serializers.ModelSerializer):
    """Serializer for RecyclingFacility model."""
    operator_name = serializers.ReadOnlyField(source='operator.get_full_name')
    accepted_materials_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RecyclingFacility
        fields = (
            'id', 'name', 'operator', 'operator_name', 'address', 'latitude',
            'longitude', 'contact_email', 'contact_phone', 'capacity',
            'operating_hours', 'accepted_materials', 'accepted_materials_count',
            'certifications', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'accepted_materials_count')
    
    def get_accepted_materials_count(self, obj):
        """Get count of accepted materials."""
        return obj.accepted_materials.count()


class BatchInputSerializer(serializers.ModelSerializer):
    """Serializer for BatchInput model."""
    material_name = serializers.ReadOnlyField(source='material.name')
    
    class Meta:
        model = BatchInput
        fields = (
            'id', 'material', 'material_name', 'weight', 'quality_grade',
            'contamination_level', 'source', 'collection_item', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class BatchOutputSerializer(serializers.ModelSerializer):
    """Serializer for BatchOutput model."""
    material_name = serializers.ReadOnlyField(source='material.name')
    
    class Meta:
        model = BatchOutput
        fields = (
            'id', 'material', 'material_name', 'weight', 'quality_grade',
            'destination', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class RecyclingBatchSerializer(serializers.ModelSerializer):
    """Serializer for RecyclingBatch model."""
    facility_name = serializers.ReadOnlyField(source='facility.name')
    inputs = BatchInputSerializer(many=True, read_only=True)
    outputs = BatchOutputSerializer(many=True, read_only=True)
    efficiency = serializers.SerializerMethodField()
    
    class Meta:
        model = RecyclingBatch
        fields = (
            'id', 'facility', 'facility_name', 'batch_number', 'status',
            'start_date', 'end_date', 'total_input_weight', 'total_output_weight',
            'yield_rate', 'energy_consumed', 'water_consumed', 'notes',
            'inputs', 'outputs', 'efficiency', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'efficiency')
    
    def get_efficiency(self, obj):
        """Get recycling efficiency percentage."""
        return obj.calculate_efficiency()


class RecyclingBatchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a RecyclingBatch with inputs and outputs."""
    inputs = BatchInputSerializer(many=True)
    outputs = BatchOutputSerializer(many=True, required=False)
    
    class Meta:
        model = RecyclingBatch
        fields = (
            'facility', 'batch_number', 'status', 'start_date', 'end_date',
            'total_input_weight', 'total_output_weight', 'yield_rate',
            'energy_consumed', 'water_consumed', 'notes', 'inputs', 'outputs'
        )
    
    def create(self, validated_data):
        """Create a RecyclingBatch with nested inputs and outputs."""
        inputs_data = validated_data.pop('inputs')
        outputs_data = validated_data.pop('outputs', [])
        batch = RecyclingBatch.objects.create(**validated_data)
        
        for input_data in inputs_data:
            BatchInput.objects.create(batch=batch, **input_data)
            
        for output_data in outputs_data:
            BatchOutput.objects.create(batch=batch, **output_data)
            
        return batch 