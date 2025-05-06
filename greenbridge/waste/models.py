"""
Models for the Waste Management app.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from greenbridge.utils.mixins import TimeStampedModel, SoftDeleteModel, AuditableModel, OwnedModel
from greenbridge.utils.validators import validate_waste_code, validate_positive_number
from greenbridge.utils.fields import WeightField, UUIDField
import uuid


class WasteCategory(TimeStampedModel, SoftDeleteModel):
    """
    Categories of waste materials that can be recycled.
    Examples: Plastics, Glass, Metals, Electronics, etc.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=10, unique=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='subcategories', verbose_name=_('parent category')
    )
    recyclable = models.BooleanField(_('recyclable'), default=True)
    hazardous = models.BooleanField(_('hazardous'), default=False)
    image = models.ImageField(_('image'), upload_to='waste_categories/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('waste category')
        verbose_name_plural = _('waste categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_path(self):
        """
        Get the full hierarchical path of the category.
        Example: "Electronics > Computers > Laptops"
        """
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Material(TimeStampedModel, SoftDeleteModel):
    """
    Specific materials that can be recycled.
    Examples: PET, HDPE, Aluminum, etc.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(
        WasteCategory, on_delete=models.CASCADE,
        related_name='materials', verbose_name=_('category')
    )
    recyclable = models.BooleanField(_('recyclable'), default=True)
    value_per_kg = models.DecimalField(
        _('value per kg'), max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    co2_offset_per_kg = models.DecimalField(
        _('CO2 offset per kg'), max_digits=10, decimal_places=2,
        null=True, blank=True, help_text=_('CO2 emission reduction in kg')
    )
    image = models.ImageField(_('image'), upload_to='materials/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('material')
        verbose_name_plural = _('materials')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class WasteCollection(TimeStampedModel, AuditableModel, OwnedModel):
    """
    Record of waste collection events.
    Can be created by brands, recyclers, or citizens.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    )
    
    id = UUIDField()
    collection_date = models.DateTimeField(_('collection date'))
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    location_name = models.CharField(_('location name'), max_length=255)
    address = models.TextField(_('address'))
    latitude = models.FloatField(_('latitude'), null=True, blank=True)
    longitude = models.FloatField(_('longitude'), null=True, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    recycler = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='recycler_collections',
        verbose_name=_('recycler')
    )
    brand = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='brand_collections',
        verbose_name=_('brand')
    )
    custom_collection_code = models.CharField(
        _('custom collection code'), max_length=20, blank=True,
        help_text=_('Custom identifier for the collection')
    )
    
    class Meta:
        verbose_name = _('waste collection')
        verbose_name_plural = _('waste collections')
        ordering = ['-collection_date']
    
    def __str__(self):
        return f"Collection at {self.location_name} on {self.collection_date}"
    
    @property
    def total_weight(self):
        """Calculate total weight of all items in this collection."""
        return self.items.aggregate(
            total=models.Sum('weight')
        )['total'] or 0
    
    @property
    def unique_materials(self):
        """Get list of unique materials in this collection."""
        return Material.objects.filter(
            id__in=self.items.values_list('material', flat=True)
        ).distinct()


class CollectionItem(TimeStampedModel):
    """
    Individual items within a waste collection.
    """
    id = UUIDField()
    collection = models.ForeignKey(
        WasteCollection, on_delete=models.CASCADE,
        related_name='items', verbose_name=_('collection')
    )
    material = models.ForeignKey(
        Material, on_delete=models.PROTECT,
        related_name='collection_items', verbose_name=_('material')
    )
    weight = WeightField(_('weight'))
    quantity = models.PositiveIntegerField(
        _('quantity'), default=1,
        validators=[validate_positive_number]
    )
    waste_code = models.CharField(
        _('waste code'), max_length=10, blank=True,
        validators=[validate_waste_code]
    )
    notes = models.TextField(_('notes'), blank=True)
    image = models.ImageField(_('image'), upload_to='collection_items/', null=True, blank=True)
    
    class Meta:
        verbose_name = _('collection item')
        verbose_name_plural = _('collection items')
    
    def __str__(self):
        return f"{self.material.name} - {self.weight}kg"
    
    @property
    def total_value(self):
        """Calculate the monetary value of this item."""
        if self.material.value_per_kg:
            return self.weight * self.material.value_per_kg
        return 0
    
    @property
    def co2_offset(self):
        """Calculate the CO2 emission reduction for this item."""
        if self.material.co2_offset_per_kg:
            return self.weight * self.material.co2_offset_per_kg
        return 0


class RecyclingFacility(TimeStampedModel, SoftDeleteModel):
    """
    Recycling facilities where waste can be processed.
    """
    id = UUIDField()
    name = models.CharField(_('name'), max_length=255)
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='operated_facilities', verbose_name=_('operator')
    )
    address = models.TextField(_('address'))
    latitude = models.FloatField(_('latitude'), null=True, blank=True)
    longitude = models.FloatField(_('longitude'), null=True, blank=True)
    contact_email = models.EmailField(_('contact email'), blank=True)
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    capacity = models.PositiveIntegerField(
        _('capacity'), null=True, blank=True,
        help_text=_('Processing capacity in tons per day')
    )
    operating_hours = models.TextField(_('operating hours'), blank=True)
    accepted_materials = models.ManyToManyField(
        Material, related_name='accepted_by_facilities',
        verbose_name=_('accepted materials')
    )
    certifications = models.TextField(_('certifications'), blank=True)
    
    class Meta:
        verbose_name = _('recycling facility')
        verbose_name_plural = _('recycling facilities')
    
    def __str__(self):
        return self.name
