"""
Models for the eco cabinet app, tracking user environmental impact.
"""
import uuid
from decimal import Decimal
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, F
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField


class EcoScore(models.Model):
    """User eco score model for tracking environmental impact."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eco_score'
    )
    
    # Cumulative metrics
    total_batches = models.PositiveIntegerField(_('total batches'), default=0)
    total_weight_kg = models.DecimalField(
        _('total weight (kg)'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Environmental impact metrics
    total_co2_saved_kg = models.DecimalField(
        _('total CO2 saved (kg)'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_water_saved_liters = models.DecimalField(
        _('total water saved (liters)'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_energy_saved_kwh = models.DecimalField(
        _('total energy saved (kWh)'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Gamification elements
    level = models.PositiveIntegerField(_('level'), default=1)
    points = models.PositiveIntegerField(_('points'), default=0)
    badges = ArrayField(
        models.CharField(max_length=50),
        verbose_name=_('badges'),
        default=list,
        blank=True
    )
    next_badge_progress = models.FloatField(
        _('next badge progress'),
        default=0.0
    )
    streak_days = models.PositiveIntegerField(_('streak days'), default=0)
    longest_streak_days = models.PositiveIntegerField(_('longest streak days'), default=0)
    last_activity_date = models.DateField(_('last activity date'), null=True, blank=True)
    
    # Visualizations
    trees_equivalent = models.DecimalField(
        _('trees equivalent'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Number of trees equivalent to the CO2 saved')
    )
    
    # Ranking
    global_rank = models.PositiveIntegerField(_('global rank'), null=True, blank=True)
    region_rank = models.PositiveIntegerField(_('region rank'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('eco score')
        verbose_name_plural = _('eco scores')
        indexes = [
            models.Index(fields=['-total_weight_kg']),
            models.Index(fields=['-level']),
            models.Index(fields=['-points']),
        ]

    def __str__(self):
        return f"EcoScore for {self.user.email}"
    
    def update_from_batches(self):
        """Update eco score metrics based on user's batches."""
        from greenbridge.waste.models import TextileBatch
        
        # Get completed batches (recycled status)
        batches = TextileBatch.objects.filter(
            owner=self.user,
            status=TextileBatch.RECYCLED,
            is_active=True
        )
        
        # Update batch count
        self.total_batches = batches.count()
        
        # Update weight
        weight_sum = batches.aggregate(total=Sum('weight_kg'))['total'] or Decimal('0.00')
        self.total_weight_kg = weight_sum
        
        # Calculate environmental impact
        impact = batches.aggregate(
            co2=Sum(F('weight_kg') * F('material_type__co2_per_kg')),
            water=Sum(F('weight_kg') * F('material_type__water_per_kg')),
            energy=Sum(F('weight_kg') * F('material_type__energy_per_kg'))
        )
        
        self.total_co2_saved_kg = impact['co2'] or Decimal('0.00')
        self.total_water_saved_liters = impact['water'] or Decimal('0.00')
        self.total_energy_saved_kwh = impact['energy'] or Decimal('0.00')
        
        # Calculate trees equivalent (1 tree absorbs ~20kg CO2 per year)
        self.trees_equivalent = self.total_co2_saved_kg / Decimal('20.00')
        
        # Update badges and level based on weight
        self._update_gamification_elements()
        
        # Update streak
        self._update_streak()
        
        self.save()
    
    def _update_gamification_elements(self):
        """Update badges, level, and points based on metrics."""
        # Update level (1kg = 10 points, level thresholds are 100, 300, 600, 1000, etc.)
        self.points = int(self.total_weight_kg * 10)
        
        level_thresholds = [0, 100, 300, 600, 1000, 1500, 2100, 2800, 3600, 4500, 5500]
        for i, threshold in enumerate(level_thresholds):
            if self.points >= threshold:
                self.level = i + 1
        
        # Update badges based on milestones
        badges = []
        
        # Weight-based badges
        if self.total_weight_kg >= Decimal('1.00'):
            badges.append('first_step')
        if self.total_weight_kg >= Decimal('10.00'):
            badges.append('eco_starter')
        if self.total_weight_kg >= Decimal('50.00'):
            badges.append('eco_enthusiast')
        if self.total_weight_kg >= Decimal('100.00'):
            badges.append('eco_warrior')
        if self.total_weight_kg >= Decimal('500.00'):
            badges.append('eco_champion')
        if self.total_weight_kg >= Decimal('1000.00'):
            badges.append('eco_legend')
        
        # Batch count badges
        if self.total_batches >= 5:
            badges.append('regular_recycler')
        if self.total_batches >= 20:
            badges.append('dedicated_recycler')
        if self.total_batches >= 50:
            badges.append('recycling_expert')
        
        # Streak badges
        if self.streak_days >= 7:
            badges.append('weekly_streak')
        if self.streak_days >= 30:
            badges.append('monthly_streak')
        if self.streak_days >= 100:
            badges.append('centurion')
        
        # Update badge list
        self.badges = list(set(badges))
        
        # Calculate progress to next badge
        next_badge_thresholds = {
            'first_step': 1,
            'eco_starter': 10,
            'eco_enthusiast': 50,
            'eco_warrior': 100,
            'eco_champion': 500,
            'eco_legend': 1000,
        }
        
        current_weight = float(self.total_weight_kg)
        
        for badge, threshold in sorted(next_badge_thresholds.items(), key=lambda x: x[1]):
            if badge not in self.badges:
                self.next_badge_progress = current_weight / threshold
                break
        else:
            self.next_badge_progress = 1.0  # All badges achieved
    
    def _update_streak(self):
        """Update the user's activity streak."""
        today = timezone.now().date()
        
        if not self.last_activity_date:
            # First activity
            self.streak_days = 1
            self.longest_streak_days = 1
            self.last_activity_date = today
        elif self.last_activity_date == today:
            # Already updated today
            pass
        elif (today - self.last_activity_date).days == 1:
            # Consecutive day
            self.streak_days += 1
            self.last_activity_date = today
            if self.streak_days > self.longest_streak_days:
                self.longest_streak_days = self.streak_days
        else:
            # Streak broken
            self.streak_days = 1
            self.last_activity_date = today


class EcoHistory(models.Model):
    """Historical eco score snapshots for tracking progress over time."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eco_history'
    )
    
    # Time period
    date = models.DateField(_('date'))
    period_type = models.CharField(
        _('period type'),
        max_length=10,
        choices=[
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('monthly', _('Monthly')),
            ('yearly', _('Yearly')),
        ]
    )
    
    # Metrics for the period
    batches_count = models.PositiveIntegerField(_('batches count'), default=0)
    weight_kg = models.DecimalField(_('weight (kg)'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    co2_saved_kg = models.DecimalField(_('CO2 saved (kg)'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    water_saved_liters = models.DecimalField(_('water saved (liters)'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    energy_saved_kwh = models.DecimalField(_('energy saved (kWh)'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Cumulative metrics at this point
    cumulative_batches = models.PositiveIntegerField(_('cumulative batches'), default=0)
    cumulative_weight_kg = models.DecimalField(_('cumulative weight (kg)'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cumulative_co2_saved_kg = models.DecimalField(_('cumulative CO2 saved (kg)'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cumulative_water_saved_liters = models.DecimalField(_('cumulative water saved (liters)'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cumulative_energy_saved_kwh = models.DecimalField(_('cumulative energy saved (kWh)'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Gamification at this point
    level = models.PositiveIntegerField(_('level'), default=1)
    points = models.PositiveIntegerField(_('points'), default=0)
    badges_count = models.PositiveIntegerField(_('badges count'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('eco history')
        verbose_name_plural = _('eco histories')
        unique_together = ('user', 'date', 'period_type')
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'period_type']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.period_type} - {self.date}"


class Achievement(models.Model):
    """Pre-defined achievements that users can earn."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(_('code'), max_length=50, unique=True)
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'))
    
    # Achievement criteria
    criteria_type = models.CharField(
        _('criteria type'),
        max_length=20,
        choices=[
            ('weight', _('Weight')),
            ('batches', _('Batches')),
            ('streak', _('Streak')),
            ('material', _('Material Type')),
            ('location', _('Location')),
            ('special', _('Special')),
        ]
    )
    criteria_value = models.DecimalField(_('criteria value'), max_digits=10, decimal_places=2, null=True, blank=True)
    criteria_details = models.JSONField(_('criteria details'), null=True, blank=True)
    
    # Visual elements
    icon = models.CharField(_('icon'), max_length=50)
    color = models.CharField(_('color'), max_length=20, default='#28a745')
    
    # Reward
    points_reward = models.PositiveIntegerField(_('points reward'), default=0)
    
    # Metadata
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('achievement')
        verbose_name_plural = _('achievements')

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Achievements earned by users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements'
    )
    earned_at = models.DateTimeField(_('earned at'), auto_now_add=True)
    
    # Optional reference to what triggered the achievement
    batch = models.ForeignKey(
        'waste.TextileBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_achievements'
    )
    
    # Flag if the user has viewed/acknowledged this achievement
    is_viewed = models.BooleanField(_('viewed'), default=False)
    
    class Meta:
        verbose_name = _('user achievement')
        verbose_name_plural = _('user achievements')
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.email} - {self.achievement.name}"


# Signal to create an EcoScore instance for new users
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_eco_score(sender, instance, created, **kwargs):
    """Create an EcoScore instance for new users."""
    if created:
        EcoScore.objects.create(user=instance) 