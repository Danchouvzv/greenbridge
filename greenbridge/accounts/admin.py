"""
Admin configuration for the Accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('Profile')
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_verified')
    list_filter = ('is_active', 'is_staff', 'is_verified', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')
    inlines = (UserProfileInline,)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'profile_image', 'phone_number', 'address', 'bio')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_verified', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active', 'is_verified'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = ('user', 'company_name', 'industry')
    search_fields = ('user__email', 'company_name', 'website')
    list_filter = ('user__role', 'industry')
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Organization Info'), {'fields': ('company_name', 'website', 'registration_number', 'tax_id', 
                                            'founding_year', 'employee_count', 'industry')}),
        (_('Brand Info'), {'fields': ('sustainability_goals', 'product_categories')}),
        (_('Recycler Info'), {'fields': ('recycling_capacity', 'materials_handled', 'certification_info')}),
        (_('Charity Info'), {'fields': ('charity_type', 'mission_statement')}),
    ) 