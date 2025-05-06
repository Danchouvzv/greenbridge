"""
Admin configuration for the Geospatial app.
"""
from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.translation import gettext_lazy as _
from .models import Location, ServiceArea, CollectionRoute, RoutePoint, DropoffPoint


class RoutePointInline(admin.TabularInline):
    """Inline admin for RoutePoint."""
    model = RoutePoint
    extra = 1
    fields = ('sequence', 'point', 'arrival_time', 'departure_time')


@admin.register(Location)
class LocationAdmin(GISModelAdmin):
    """Admin configuration for Location model."""
    list_display = ('name', 'address', 'elevation', 'is_deleted')
    list_filter = ('is_deleted',)
    search_fields = ('name', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'address', 'point', 'elevation')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        }),
    )


@admin.register(ServiceArea)
class ServiceAreaAdmin(GISModelAdmin):
    """Admin configuration for ServiceArea model."""
    list_display = ('name', 'operator', 'is_deleted')
    list_filter = ('operator', 'is_deleted')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'polygon', 'operator')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        }),
    )


@admin.register(CollectionRoute)
class CollectionRouteAdmin(GISModelAdmin):
    """Admin configuration for CollectionRoute model."""
    list_display = ('name', 'operator', 'distance', 'estimated_duration', 'point_count', 'is_optimized')
    list_filter = ('operator', 'is_optimized', 'is_deleted')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'point_count')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'line', 'operator')
        }),
        (_('Route Details'), {
            'fields': ('distance', 'estimated_duration', 'start_time', 'end_time', 'is_optimized')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        }),
    )
    inlines = [RoutePointInline]


@admin.register(RoutePoint)
class RoutePointAdmin(GISModelAdmin):
    """Admin configuration for RoutePoint model."""
    list_display = ('route', 'sequence', 'arrival_time', 'departure_time')
    list_filter = ('route',)
    search_fields = ('route__name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('route', 'point', 'sequence', 'arrival_time', 'departure_time')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(DropoffPoint)
class DropoffPointAdmin(GISModelAdmin):
    """Admin configuration for DropoffPoint model."""
    list_display = ('name', 'operator', 'address', 'is_active', 'is_deleted')
    list_filter = ('operator', 'is_active', 'is_deleted')
    search_fields = ('name', 'address', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('accepted_materials',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'point', 'address', 'operator')
        }),
        (_('Contact Information'), {
            'fields': ('operating_hours', 'contact_phone', 'contact_email', 'website')
        }),
        (_('Materials & Status'), {
            'fields': ('is_active', 'accepted_materials')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        }),
    ) 