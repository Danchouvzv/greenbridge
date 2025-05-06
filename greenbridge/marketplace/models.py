"""
Models for the marketplace app, handling listings and deals for textile exchange.
"""
import uuid
from decimal import Decimal
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Listing(models.Model):
    """Model for material listings in the marketplace."""

    # Status choices
    DRAFT = 'draft'
    ACTIVE = 'active'
    RESERVED = 'reserved'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'

    STATUS_CHOICES = [
        (DRAFT, _('Draft')),
        (ACTIVE, _('Active')),
        (RESERVED, _('Reserved')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
        (EXPIRED, _('Expired')),
    ]

    # Availability types
    IMMEDIATE = 'immediate'
    SCHEDULED = 'scheduled'
    ON_DEMAND = 'on_demand'

    AVAILABILITY_CHOICES = [
        (IMMEDIATE, _('Immediate')),
        (SCHEDULED, _('Scheduled')),
        (ON_DEMAND, _('On Demand')),
    ]

    # Pricing types
    FIXED = 'fixed'
    NEGOTIABLE = 'negotiable'
    AUCTION = 'auction'
    FREE = 'free'

    PRICING_TYPE_CHOICES = [
        (FIXED, _('Fixed')),
        (NEGOTIABLE, _('Negotiable')),
        (AUCTION, _('Auction')),
        (FREE, _('Free')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('title'), max_length=255)
    
    # Ownership
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.CASCADE,
        related_name='listings'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_listings'
    )
    
    # Material details
    material_type = models.ForeignKey(
        'waste.MaterialType',
        on_delete=models.PROTECT,
        related_name='listings'
    )
    description = models.TextField(_('description'))
    condition = models.CharField(_('condition'), max_length=100)
    quantity_kg = models.DecimalField(
        _('quantity (kg)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    minimum_order_kg = models.DecimalField(
        _('minimum order (kg)'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        null=True,
        blank=True
    )
    quality_certificate = models.CharField(_('quality certificate'), max_length=100, blank=True)
    color = models.CharField(_('color'), max_length=50, blank=True)
    composition = models.TextField(_('composition'), blank=True)
    
    # Media
    photos = models.ManyToManyField(
        'ListingPhoto',
        related_name='listings',
        blank=True
    )
    
    # Pricing
    pricing_type = models.CharField(_('pricing type'), max_length=20, choices=PRICING_TYPE_CHOICES, default=FIXED)
    price_per_kg = models.DecimalField(
        _('price per kg'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(_('currency'), max_length=3, default='KZT')
    
    # Location
    location = models.PointField(_('location'), geography=True, null=True, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state_province = models.CharField(_('state/province'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100)
    
    # Availability
    availability_type = models.CharField(
        _('availability type'),
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default=IMMEDIATE
    )
    available_from = models.DateField(_('available from'), null=True, blank=True)
    available_until = models.DateField(_('available until'), null=True, blank=True)
    
    # Logistics
    delivery_options = models.JSONField(
        _('delivery options'),
        null=True,
        blank=True,
        help_text=_('JSON array of available delivery options and costs')
    )
    delivery_included = models.BooleanField(_('delivery included'), default=False)
    
    # Status and visibility
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    is_featured = models.BooleanField(_('featured'), default=False)
    is_verified = models.BooleanField(_('verified'), default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_listings'
    )
    verification_date = models.DateTimeField(_('verification date'), null=True, blank=True)
    
    # Statistics
    view_count = models.PositiveIntegerField(_('view count'), default=0)
    inquiry_count = models.PositiveIntegerField(_('inquiry count'), default=0)
    
    # Tags
    tags = models.CharField(_('tags'), max_length=255, blank=True)
    
    # Dates
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    # Batch reference (optional)
    batch = models.ForeignKey(
        'waste.TextileBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listings'
    )
    
    # Soft delete
    is_active = models.BooleanField(_('active'), default=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('listing')
        verbose_name_plural = _('listings')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['material_type']),
            models.Index(fields=['city', 'country']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_active']),
        ]
        permissions = [
            ('verify_listing', _('Can verify listing')),
            ('feature_listing', _('Can feature listing')),
        ]

    def __str__(self):
        return f"{self.title} - {self.quantity_kg}kg ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps and status."""
        # Set published_at when status changes to ACTIVE
        if self.pk is not None:
            old_instance = Listing.objects.get(pk=self.pk)
            if old_instance.status != self.status and self.status == self.ACTIVE and not self.published_at:
                self.published_at = timezone.now()
        elif self.status == self.ACTIVE and not self.published_at:
            self.published_at = timezone.now()
            
        # Set verification date when verified
        if self.is_verified and not self.verification_date:
            self.verification_date = timezone.now()
            
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Soft delete the listing."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])
    
    def increment_view_count(self):
        """Increment the view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_inquiry_count(self):
        """Increment the inquiry count."""
        self.inquiry_count += 1
        self.save(update_fields=['inquiry_count'])
    
    @property
    def total_price(self):
        """Calculate the total price of the listing."""
        if self.price_per_kg and self.quantity_kg:
            return self.price_per_kg * self.quantity_kg
        return None
    
    @property
    def is_available(self):
        """Check if the listing is currently available."""
        if self.status != self.ACTIVE:
            return False
            
        today = timezone.now().date()
        
        if self.available_from and self.available_from > today:
            return False
            
        if self.available_until and self.available_until < today:
            return False
            
        return True


class ListingPhoto(models.Model):
    """Photos for listing visualization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(_('image'), upload_to='listings/photos/')
    caption = models.CharField(_('caption'), max_length=255, blank=True)
    is_primary = models.BooleanField(_('primary'), default=False)
    order = models.PositiveSmallIntegerField(_('order'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_listing_photos'
    )
    
    class Meta:
        verbose_name = _('listing photo')
        verbose_name_plural = _('listing photos')
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Photo for {self.caption or 'Listing'}"


class Deal(models.Model):
    """Model for deals between organizations."""

    # Status choices
    DRAFT = 'draft'
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    DISPUTED = 'disputed'

    STATUS_CHOICES = [
        (DRAFT, _('Draft')),
        (PENDING, _('Pending')),
        (ACCEPTED, _('Accepted')),
        (IN_PROGRESS, _('In Progress')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
        (DISPUTED, _('Disputed')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_code = models.CharField(_('reference code'), max_length=20, unique=True)
    
    # Parties
    seller = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.PROTECT,
        related_name='selling_deals'
    )
    buyer = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.PROTECT,
        related_name='buying_deals'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_deals'
    )
    
    # Deal details
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    
    # Related listing
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals'
    )
    
    # Material details
    material_type = models.ForeignKey(
        'waste.MaterialType',
        on_delete=models.PROTECT,
        related_name='deals'
    )
    quantity_kg = models.DecimalField(_('quantity (kg)'), max_digits=10, decimal_places=2)
    
    # Financial details
    price_per_kg = models.DecimalField(_('price per kg'), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_('total amount'), max_digits=12, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='KZT')
    payment_terms = models.TextField(_('payment terms'), blank=True)
    payment_due_date = models.DateField(_('payment due date'), null=True, blank=True)
    payment_status = models.CharField(
        _('payment status'),
        max_length=20,
        choices=[
            ('unpaid', _('Unpaid')),
            ('partial', _('Partially Paid')),
            ('paid', _('Paid')),
            ('refunded', _('Refunded')),
        ],
        default='unpaid'
    )
    
    # Delivery details
    delivery_method = models.CharField(_('delivery method'), max_length=100, blank=True)
    delivery_cost = models.DecimalField(
        _('delivery cost'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    pickup_address = models.CharField(_('pickup address'), max_length=255, blank=True)
    delivery_address = models.CharField(_('delivery address'), max_length=255, blank=True)
    estimated_delivery_date = models.DateField(_('estimated delivery date'), null=True, blank=True)
    actual_delivery_date = models.DateField(_('actual delivery date'), null=True, blank=True)
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    
    # Dates
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    accepted_at = models.DateTimeField(_('accepted at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    cancelled_at = models.DateTimeField(_('cancelled at'), null=True, blank=True)
    
    # Terms and notes
    terms_accepted_seller = models.BooleanField(_('terms accepted by seller'), default=False)
    terms_accepted_buyer = models.BooleanField(_('terms accepted by buyer'), default=False)
    notes = models.TextField(_('notes'), blank=True)
    
    # Documents
    contract_document = models.FileField(
        _('contract document'),
        upload_to='deals/contracts/',
        null=True,
        blank=True
    )
    
    # Dispute information
    dispute_reason = models.TextField(_('dispute reason'), blank=True)
    dispute_opened_by = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opened_disputes'
    )
    dispute_resolution = models.TextField(_('dispute resolution'), blank=True)
    dispute_resolved_at = models.DateTimeField(_('dispute resolved at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('deal')
        verbose_name_plural = _('deals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['seller']),
            models.Index(fields=['buyer']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['reference_code']),
        ]
        permissions = [
            ('approve_deal', _('Can approve deal')),
            ('resolve_dispute', _('Can resolve dispute')),
        ]

    def __str__(self):
        return f"{self.reference_code} - {self.seller.name} → {self.buyer.name}"
    
    def save(self, *args, **kwargs):
        """Override save to generate reference code and update timestamps."""
        # Generate reference code if not provided
        if not self.reference_code:
            # Format: D-{YY}{MM}{DD}-{random 4 digits}
            now = timezone.now()
            date_part = now.strftime('%y%m%d')
            
            # Find the latest deal created today to increment sequence
            today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time())
            today_end = timezone.datetime.combine(now.date(), timezone.datetime.max.time())
            
            # Get count of deals created today
            today_count = Deal.objects.filter(
                created_at__range=(today_start, today_end)
            ).count()
            
            # Create the sequence number (base 1)
            sequence = today_count + 1
            
            # Format: D-{YY}{MM}{DD}-{sequence}
            self.reference_code = f"D-{date_part}-{sequence:04d}"
        
        # Calculate total amount if not set
        if not self.total_amount and self.price_per_kg and self.quantity_kg:
            self.total_amount = self.price_per_kg * self.quantity_kg
            
        # Update timestamps based on status changes
        if self.pk is not None:
            old_instance = Deal.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                if self.status == self.ACCEPTED and not self.accepted_at:
                    self.accepted_at = timezone.now()
                elif self.status == self.COMPLETED and not self.completed_at:
                    self.completed_at = timezone.now()
                elif self.status == self.CANCELLED and not self.cancelled_at:
                    self.cancelled_at = timezone.now()
                    
        super().save(*args, **kwargs)
        
    @property
    def is_active(self):
        """Check if the deal is active (not completed or cancelled)."""
        return self.status not in [self.COMPLETED, self.CANCELLED, self.DISPUTED]
    
    @property
    def days_since_creation(self):
        """Calculate days since deal creation."""
        return (timezone.now().date() - self.created_at.date()).days


class DealEvent(models.Model):
    """Log of important events in a deal's lifecycle."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.CharField(_('event type'), max_length=50)
    description = models.TextField(_('description'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deal_events'
    )
    organization = models.ForeignKey(
        'accounts.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deal_events'
    )
    additional_data = models.JSONField(_('additional data'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('deal event')
        verbose_name_plural = _('deal events')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.deal.reference_code} - {self.event_type} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# Signal to create a deal event when a deal status changes
@receiver(post_save, sender=Deal)
def create_deal_event(sender, instance, created, **kwargs):
    """Create a deal event when a deal's status changes."""
    if created:
        DealEvent.objects.create(
            deal=instance,
            event_type='created',
            description=f"Deal {instance.reference_code} created",
            created_by=instance.created_by,
            organization=instance.seller
        )
    else:
        try:
            old_instance = Deal.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                DealEvent.objects.create(
                    deal=instance,
                    event_type=f"status_changed_to_{instance.status}",
                    description=f"Deal status changed from {old_instance.get_status_display()} to {instance.get_status_display()}",
                    # Note: created_by would need to be set from the view
                    # Use seller organization as default
                    organization=instance.seller
                )
        except Deal.DoesNotExist:
            pass 