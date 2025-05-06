"""
Models for the locations app, handling collection points and geospatial data.
"""
import uuid
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class Region(models.Model):
    """Region model for geographic areas."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    code = models.CharField(_('code'), max_length=20, unique=True)
    
    # Geospatial data - multipolygon for complex boundaries
    boundary = models.MultiPolygonField(_('boundary'), geography=True, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    
    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('regions')
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name


class CollectionPoint(models.Model):
    """Collection point for textile waste."""

    # Status choices
    PENDING = 'pending'
    ACTIVE = 'active'
    TEMPORARY = 'temporary'
    MAINTENANCE = 'maintenance'
    INACTIVE = 'inactive'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (ACTIVE, _('Active')),
        (TEMPORARY, _('Temporary')),
        (MAINTENANCE, _('Under Maintenance')),
        (INACTIVE, _('Inactive')),
    ]
    
    # Verification status
    UNVERIFIED = 'unverified'
    VERIFIED = 'verified'
    FEATURED = 'featured'
    
    VERIFICATION_CHOICES = [
        (UNVERIFIED, _('Unverified')),
        (VERIFIED, _('Verified')),
        (FEATURED, _('Featured')),
    ]
    
    # Collection point type
    PERMANENT = 'permanent'
    POP_UP = 'pop_up'
    MOBILE = 'mobile'
    RETAIL = 'retail'
    COMMUNITY = 'community'
    
    TYPE_CHOICES = [
        (PERMANENT, _('Permanent')),
        (POP_UP, _('Pop-up')),
        (MOBILE, _('Mobile')),
        (RETAIL, _('Retail')),
        (COMMUNITY, _('Community')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    
    # Type and status
    point_type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES, default=PERMANENT)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    verification_status = models.CharField(
        _('verification status'),
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=UNVERIFIED
    )
    
    # Location
    location = models.PointField(_('location'), geography=True)
    address = models.CharField(_('address'), max_length=255)
    city = models.CharField(_('city'), max_length=100)
    state_province = models.CharField(_('state/province'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collection_points'
    )
    
    # Details
    description = models.TextField(_('description'), blank=True)
    instructions = models.TextField(_('instructions'), blank=True)
    accepted_materials = ArrayField(
        models.CharField(max_length=50),
        verbose_name=_('accepted materials'),
        blank=True,
        default=list
    )
    capacity_kg = models.PositiveIntegerField(
        _('capacity (kg)'),
        null=True,
        blank=True,
        help_text=_('Maximum capacity in kilograms')
    )
    current_fill_level = models.FloatField(
        _('current fill level'),
        default=0.0,
        help_text=_('Current fill level as a percentage (0-100)')
    )
    
    # Opening hours - stored as JSON with day-of-week keys
    opening_hours = models.JSONField(
        _('opening hours'),
        null=True,
        blank=True,
        help_text=_('Opening hours in JSON format')
    )
    is_24h = models.BooleanField(_('24-hour operation'), default=False)
    
    # Contact
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    contact_email = models.EmailField(_('contact email'), blank=True)
    website = models.URLField(_('website'), blank=True)
    
    # Media
    photos = ArrayField(
        models.URLField(),
        verbose_name=_('photos'),
        blank=True,
        default=list
    )
    
    # Management
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_collection_points'
    )
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_collection_points'
    )
    
    # For temporary or mobile collection points
    active_from = models.DateTimeField(_('active from'), null=True, blank=True)
    active_until = models.DateTimeField(_('active until'), null=True, blank=True)
    
    # Statistics
    total_collections = models.PositiveIntegerField(_('total collections'), default=0)
    total_weight_collected_kg = models.DecimalField(
        _('total weight collected (kg)'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    last_collection_date = models.DateTimeField(_('last collection date'), null=True, blank=True)
    
    # Ratings and popularity
    average_rating = models.FloatField(_('average rating'), default=0.0)
    rating_count = models.PositiveIntegerField(_('rating count'), default=0)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_collection_points'
    )
    
    # Soft delete
    is_active = models.BooleanField(_('active'), default=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('collection point')
        verbose_name_plural = _('collection points')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['point_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['verification_status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"
    
    def soft_delete(self, user=None):
        """Soft delete the collection point."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])
    
    @property
    def is_open_now(self):
        """Check if the collection point is currently open."""
        if self.is_24h:
            return True
            
        if not self.opening_hours:
            return False
            
        now = timezone.now()
        day_of_week = now.strftime('%A').lower()
        
        if day_of_week not in self.opening_hours:
            return False
            
        current_time = now.strftime('%H:%M')
        
        for time_range in self.opening_hours.get(day_of_week, []):
            if time_range.get('from', '') <= current_time <= time_range.get('to', ''):
                return True
                
        return False
    
    @property
    def is_temporary_active(self):
        """Check if a temporary collection point is currently active."""
        if self.point_type != self.TEMPORARY and self.point_type != self.POP_UP:
            return True
            
        now = timezone.now()
        
        if self.active_from and self.active_until:
            return self.active_from <= now <= self.active_until
            
        return False


class CollectionPointReview(models.Model):
    """User reviews for collection points."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection_point = models.ForeignKey(
        CollectionPoint,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collection_point_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        _('rating'),
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]
    )
    comment = models.TextField(_('comment'), blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Moderation
    is_approved = models.BooleanField(_('approved'), default=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews'
    )
    moderation_note = models.TextField(_('moderation note'), blank=True)
    
    class Meta:
        verbose_name = _('collection point review')
        verbose_name_plural = _('collection point reviews')
        unique_together = ('collection_point', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.collection_point.name} by {self.user.email}"
    
    def save(self, *args, **kwargs):
        """Override save to update collection point rating."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update collection point rating
        if is_new or self._state.adding:
            self._update_collection_point_rating()
    
    def _update_collection_point_rating(self):
        """Update the average rating and rating count for the collection point."""
        approved_reviews = self.collection_point.reviews.filter(is_approved=True)
        count = approved_reviews.count()
        
        if count > 0:
            avg_rating = approved_reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.collection_point.average_rating = round(avg_rating, 1)
        else:
            self.collection_point.average_rating = 0.0
            
        self.collection_point.rating_count = count
        self.collection_point.save(update_fields=['average_rating', 'rating_count'])


class Route(models.Model):
    """Model for saved routes between locations."""

    # Mode of transport
    WALKING = 'walking'
    CYCLING = 'cycling'
    DRIVING = 'driving'
    PUBLIC_TRANSPORT = 'public_transport'
    
    MODE_CHOICES = [
        (WALKING, _('Walking')),
        (CYCLING, _('Cycling')),
        (DRIVING, _('Driving')),
        (PUBLIC_TRANSPORT, _('Public Transport')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_routes'
    )
    
    # Route details
    name = models.CharField(_('name'), max_length=100)
    from_location = models.PointField(_('from location'), geography=True)
    from_address = models.CharField(_('from address'), max_length=255)
    to_location = models.PointField(_('to location'), geography=True)
    to_address = models.CharField(_('to address'), max_length=255)
    
    # Can be a route to a collection point
    collection_point = models.ForeignKey(
        CollectionPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes'
    )
    
    # Route geometry
    route_line = models.LineStringField(_('route line'), geography=True, null=True, blank=True)
    
    # Route stats
    distance_meters = models.PositiveIntegerField(_('distance (meters)'), null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(_('duration (seconds)'), null=True, blank=True)
    mode_of_transport = models.CharField(_('mode of transport'), max_length=20, choices=MODE_CHOICES, default=DRIVING)
    
    # Usage stats
    times_used = models.PositiveIntegerField(_('times used'), default=0)
    last_used = models.DateTimeField(_('last used'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('route')
        verbose_name_plural = _('routes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.from_address} → {self.to_address})"
    
    def record_usage(self):
        """Record that this route was used."""
        self.times_used += 1
        self.last_used = timezone.now()
        self.save(update_fields=['times_used', 'last_used'])
    
    @property
    def distance_km(self):
        """Return distance in km."""
        return self.distance_meters / 1000 if self.distance_meters else None
    
    @property
    def duration_minutes(self):
        """Return duration in minutes."""
        return self.duration_seconds / 60 if self.duration_seconds else None 