"""
User models for the GreenBridge application.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from greenbridge.utils.mixins import TimeStampedModel, SoftDeleteModel
from greenbridge.utils.validators import validate_phone_number
import uuid


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, SoftDeleteModel):
    """
    Custom User model for GreenBridge.
    
    Uses email as the unique identifier instead of username.
    Includes role-based access control and extended profile information.
    """
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('brand', 'Brand'),
        ('recycler', 'Recycler'),
        ('charity', 'Charity'),
        ('consumer', 'Consumer'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email address.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='consumer')
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
    )
    address = models.TextField(_('address'), blank=True)
    bio = models.TextField(_('bio'), blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'
    
    @property
    def is_brand(self):
        """Check if user is a brand."""
        return self.role == 'brand'
    
    @property
    def is_recycler(self):
        """Check if user is a recycler."""
        return self.role == 'recycler'
    
    @property
    def is_charity(self):
        """Check if user is a charity."""
        return self.role == 'charity'
    
    @property
    def is_consumer(self):
        """Check if user is a consumer."""
        return self.role == 'consumer'


class UserProfile(TimeStampedModel):
    """
    Extended profile for users based on their role.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    founding_year = models.PositiveIntegerField(null=True, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    # Fields for brands
    sustainability_goals = models.TextField(blank=True)
    product_categories = models.CharField(max_length=255, blank=True)
    
    # Fields for recyclers
    recycling_capacity = models.PositiveIntegerField(
        help_text="Capacity in tons per month",
        null=True, blank=True
    )
    materials_handled = models.CharField(max_length=255, blank=True)
    certification_info = models.TextField(blank=True)
    
    # Fields for charities
    charity_type = models.CharField(max_length=100, blank=True)
    mission_statement = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class Organization(models.Model):
    """Organization model for brands, recyclers, and charities."""

    # Organization type choices
    BRAND = 'brand'
    RECYCLER = 'recycler'
    CHARITY = 'charity'

    TYPE_CHOICES = [
        (BRAND, _('Brand')),
        (RECYCLER, _('Recycler')),
        (CHARITY, _('Charity')),
    ]

    # Verification status choices
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (VERIFIED, _('Verified')),
        (REJECTED, _('Rejected')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('name'), max_length=100)
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Business details
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    registration_number = models.CharField(_('registration number'), max_length=50, blank=True)
    website = models.URLField(_('website'), blank=True)
    foundation_date = models.DateField(_('foundation date'), null=True, blank=True)
    
    # Contact information
    primary_contact_name = models.CharField(_('primary contact name'), max_length=100, blank=True)
    primary_contact_email = models.EmailField(_('primary contact email'), blank=True)
    primary_contact_phone = models.CharField(_('primary contact phone'), max_length=20, blank=True)
    
    # Address fields (encrypted in production)
    address_line1 = models.CharField(_('address line 1'), max_length=100, blank=True)
    address_line2 = models.CharField(_('address line 2'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state_province = models.CharField(_('state/province'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    
    # Geolocation
    location = models.PointField(_('location'), geography=True, null=True, blank=True)
    
    # Media
    logo = models.ImageField(upload_to='organizations/logos/', null=True, blank=True)
    banner = models.ImageField(upload_to='organizations/banners/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    created_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_organizations'
    )
    
    # Verification
    verification_date = models.DateTimeField(_('verification date'), null=True, blank=True)
    verified_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_organizations'
    )
    rejection_reason = models.TextField(_('rejection reason'), blank=True)
    
    # Soft delete
    is_active = models.BooleanField(_('active'), default=True)
    deleted_at = models.DateTimeField(_('deleted at'), null=True, blank=True)

    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')
        permissions = [
            ('verify_organization', _('Can verify organization')),
            ('reject_organization', _('Can reject organization')),
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Override save to add verification date when status changes to verified."""
        if self.pk:
            old_instance = Organization.objects.get(pk=self.pk)
            if old_instance.status != self.status and self.status == self.VERIFIED:
                self.verification_date = timezone.now()
        super().save(*args, **kwargs)
    
    def soft_delete(self, user=None):
        """Soft delete the organization."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])


class OrganizationMember(models.Model):
    """Manages organization memberships with roles."""

    # Role choices
    ADMIN = 'admin'
    MEMBER = 'member'
    VIEWER = 'viewer'

    ROLE_CHOICES = [
        (ADMIN, _('Administrator')),
        (MEMBER, _('Member')),
        (VIEWER, _('Viewer')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='organization_members'
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default=MEMBER)
    title = models.CharField(_('title'), max_length=100, blank=True)
    department = models.CharField(_('department'), max_length=100, blank=True)
    joined_at = models.DateTimeField(_('joined at'), auto_now_add=True)
    invited_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_invitations'
    )
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('organization member')
        verbose_name_plural = _('organization members')
        unique_together = ('organization', 'user')
        permissions = [
            ('change_member_role', _('Can change member role')),
            ('remove_member', _('Can remove member')),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.get_role_display()})"


class UserToken(models.Model):
    """Model for storing verification, password reset, and other tokens."""

    # Token type choices
    EMAIL_VERIFICATION = 'email_verification'
    PASSWORD_RESET = 'password_reset'
    PHONE_VERIFICATION = 'phone_verification'
    INVITATION = 'invitation'

    TOKEN_TYPE_CHOICES = [
        (EMAIL_VERIFICATION, _('Email Verification')),
        (PASSWORD_RESET, _('Password Reset')),
        (PHONE_VERIFICATION, _('Phone Verification')),
        (INVITATION, _('Invitation')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='tokens',
        null=True,
        blank=True,
    )
    email = models.EmailField(_('email address'), blank=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    token_type = models.CharField(_('token type'), max_length=50, choices=TOKEN_TYPE_CHOICES)
    token = models.CharField(_('token'), max_length=255, unique=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    expires_at = models.DateTimeField(_('expires at'))
    is_used = models.BooleanField(_('used'), default=False)
    used_at = models.DateTimeField(_('used at'), null=True, blank=True)

    class Meta:
        verbose_name = _('user token')
        verbose_name_plural = _('user tokens')
        indexes = [
            models.Index(fields=['token', 'token_type']),
            models.Index(fields=['user', 'token_type']),
            models.Index(fields=['email', 'token_type']),
        ]

    def __str__(self):
        return f"{self.get_token_type_display()} for {self.user or self.email or self.phone}"

    def mark_as_used(self):
        """Mark token as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])

    def is_valid(self):
        """Check if token is valid (not expired and not used)."""
        return not self.is_used and self.expires_at > timezone.now() 