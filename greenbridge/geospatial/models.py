"""
Models for the Geospatial app.
"""
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from greenbridge.utils.mixins import TimeStampedModel, SoftDeleteModel
from greenbridge.utils.fields import UUIDField
import uuid


class Location(TimeStampedModel, SoftDeleteModel):
    """
    Represents a geographical location with a point geometry.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=255)
    address = models.TextField(_('address'))
    point = gis_models.PointField(_('point'), geography=True)
    elevation = models.FloatField(_('elevation'), null=True, blank=True, help_text=_('Elevation in meters'))
    
    class Meta:
        verbose_name = _('location')
        verbose_name_plural = _('locations')
    
    def __str__(self):
        return self.name


class ServiceArea(TimeStampedModel, SoftDeleteModel):
    """
    Represents a geographical service area with a polygon geometry.
    Used for defining recycling service areas, collection zones, etc.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    polygon = gis_models.PolygonField(_('polygon'), geography=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='service_areas', verbose_name=_('operator')
    )
    
    class Meta:
        verbose_name = _('service area')
        verbose_name_plural = _('service areas')
    
    def __str__(self):
        return self.name


class RoutePoint(TimeStampedModel):
    """
    Represents a point in a collection route.
    """
    id = UUIDField()
    route = models.ForeignKey(
        'CollectionRoute', on_delete=models.CASCADE,
        related_name='points', verbose_name=_('route')
    )
    point = gis_models.PointField(_('point'), geography=True)
    sequence = models.PositiveIntegerField(_('sequence'))
    arrival_time = models.DateTimeField(_('arrival time'), null=True, blank=True)
    departure_time = models.DateTimeField(_('departure time'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('route point')
        verbose_name_plural = _('route points')
        ordering = ['route', 'sequence']
    
    def __str__(self):
        return f"{self.route.name} - Point {self.sequence}"


class CollectionRoute(TimeStampedModel, SoftDeleteModel):
    """
    Represents a collection route with line string geometry.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    line = gis_models.LineStringField(_('line'), geography=True, null=True, blank=True)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='routes', verbose_name=_('operator')
    )
    distance = models.FloatField(_('distance'), null=True, blank=True, help_text=_('Distance in kilometers'))
    estimated_duration = models.DurationField(_('estimated duration'), null=True, blank=True)
    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)
    is_optimized = models.BooleanField(_('is optimized'), default=False)
    
    class Meta:
        verbose_name = _('collection route')
        verbose_name_plural = _('collection routes')
    
    def __str__(self):
        return self.name
    
    @property
    def point_count(self):
        """Get count of points in this route."""
        return self.points.count()


class DropoffPoint(TimeStampedModel, SoftDeleteModel):
    """
    Represents a waste dropoff point with a point geometry.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    point = gis_models.PointField(_('point'), geography=True)
    address = models.TextField(_('address'))
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='dropoff_points', verbose_name=_('operator')
    )
    operating_hours = models.TextField(_('operating hours'), blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    contact_email = models.EmailField(_('contact email'), blank=True)
    website = models.URLField(_('website'), blank=True)
    is_active = models.BooleanField(_('is active'), default=True)
    accepted_materials = models.ManyToManyField(
        'waste.Material', related_name='accepted_at_dropoffs',
        verbose_name=_('accepted materials')
    )
    
    class Meta:
        verbose_name = _('dropoff point')
        verbose_name_plural = _('dropoff points')
    
    def __str__(self):
        return self.name 