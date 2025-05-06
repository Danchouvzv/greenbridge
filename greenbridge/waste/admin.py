"""
Admin configuration for the Waste Management app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    WasteCategory, Material, WasteCollection, CollectionItem,
    RecyclingFacility, RecyclingBatch, BatchInput, BatchOutput
)


class CollectionItemInline(admin.TabularInline):
    """Inline admin for CollectionItem."""
    model = CollectionItem
    extra = 1
    fields = ('material', 'weight', 'quantity', 'waste_code', 'image')


@admin.register(WasteCategory)
class WasteCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for WasteCategory model."""
    list_display = ('name', 'code', 'parent', 'recyclable', 'hazardous')
    list_filter = ('recyclable', 'hazardous')
    search_fields = ('name', 'code', 'description')
    prepopulated_fields = {'code': ('name',)}
    autocomplete_fields = ['parent']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """Admin configuration for Material model."""
    list_display = ('name', 'code', 'category', 'recyclable', 'value_per_kg', 'co2_offset_per_kg')
    list_filter = ('recyclable', 'category')
    search_fields = ('name', 'code', 'description')
    prepopulated_fields = {'code': ('name',)}
    autocomplete_fields = ['category']


@admin.register(WasteCollection)
class WasteCollectionAdmin(admin.ModelAdmin):
    """Admin configuration for WasteCollection model."""
    list_display = (
        'id', 'location_name', 'collection_date', 'status', 
        'owner', 'recycler', 'brand', 'total_weight'
    )
    list_filter = ('status', 'collection_date')
    search_fields = ('location_name', 'address', 'custom_collection_code')
    readonly_fields = ('created_at', 'updated_at', 'total_weight')
    fieldsets = (
        (None, {
            'fields': ('collection_date', 'status', 'owner', 'recycler', 'brand')
        }),
        (_('Location'), {
            'fields': ('location_name', 'address', 'latitude', 'longitude')
        }),
        (_('Additional Information'), {
            'fields': ('custom_collection_code', 'notes')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
    inlines = [CollectionItemInline]


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    """Admin configuration for CollectionItem model."""
    list_display = ('id', 'collection', 'material', 'weight', 'quantity', 'waste_code')
    list_filter = ('collection__status', 'material')
    search_fields = ('waste_code', 'notes', 'collection__location_name')
    readonly_fields = ('created_at', 'updated_at', 'total_value', 'co2_offset')
    autocomplete_fields = ['collection', 'material']


@admin.register(RecyclingFacility)
class RecyclingFacilityAdmin(admin.ModelAdmin):
    """Admin configuration for RecyclingFacility model."""
    list_display = ('name', 'operator', 'address', 'capacity')
    list_filter = ('operator',)
    search_fields = ('name', 'address', 'contact_email')
    filter_horizontal = ('accepted_materials',)
    fieldsets = (
        (None, {
            'fields': ('name', 'operator')
        }),
        (_('Location & Contact'), {
            'fields': ('address', 'latitude', 'longitude', 'contact_email', 'contact_phone')
        }),
        (_('Capacity & Materials'), {
            'fields': ('capacity', 'operating_hours', 'accepted_materials', 'certifications')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


class BatchInputInline(admin.TabularInline):
    """Inline admin for BatchInput."""
    model = BatchInput
    extra = 1
    fields = ('material', 'weight', 'quality_grade', 'contamination_level', 'source')


class BatchOutputInline(admin.TabularInline):
    """Inline admin for BatchOutput."""
    model = BatchOutput
    extra = 1
    fields = ('material', 'weight', 'quality_grade', 'destination')


@admin.register(RecyclingBatch)
class RecyclingBatchAdmin(admin.ModelAdmin):
    """Admin configuration for RecyclingBatch model."""
    list_display = (
        'batch_number', 'facility', 'status', 'start_date', 
        'end_date', 'total_input_weight', 'total_output_weight'
    )
    list_filter = ('status', 'facility', 'start_date')
    search_fields = ('batch_number', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('facility', 'batch_number', 'status')
        }),
        (_('Timing'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Metrics'), {
            'fields': ('total_input_weight', 'total_output_weight', 'yield_rate', 
                      'energy_consumed', 'water_consumed')
        }),
        (_('Additional Information'), {
            'fields': ('notes',)
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
    inlines = [BatchInputInline, BatchOutputInline] 