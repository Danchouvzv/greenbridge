"""
Custom validators for the GreenBridge application.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_latitude(value):
    """
    Validates that a value is a valid latitude (-90 to 90).
    """
    if value < -90 or value > 90:
        raise ValidationError(
            _('%(value)s is not a valid latitude. Must be between -90 and 90.'),
            params={'value': value},
        )


def validate_longitude(value):
    """
    Validates that a value is a valid longitude (-180 to 180).
    """
    if value < -180 or value > 180:
        raise ValidationError(
            _('%(value)s is not a valid longitude. Must be between -180 and 180.'),
            params={'value': value},
        )


def validate_phone_number(value):
    """
    Validates that a value is a valid phone number.
    Accepts formats: +1234567890, (123) 456-7890, 123-456-7890
    """
    phone_regex = r'^\+?1?\d{9,15}$|^\(\d{3}\)\s\d{3}-\d{4}$|^\d{3}-\d{3}-\d{4}$'
    if not re.match(phone_regex, value):
        raise ValidationError(
            _('%(value)s is not a valid phone number.'),
            params={'value': value},
        )


def validate_waste_code(value):
    """
    Validates that a value is a valid waste code.
    Format: 2 letters followed by 4 digits (e.g., AB1234)
    """
    waste_code_regex = r'^[A-Z]{2}\d{4}$'
    if not re.match(waste_code_regex, value):
        raise ValidationError(
            _('%(value)s is not a valid waste code. Format must be: AA0000'),
            params={'value': value},
        )


def validate_positive_number(value):
    """
    Validates that a value is a positive number.
    """
    if value <= 0:
        raise ValidationError(
            _('%(value)s is not a positive number.'),
            params={'value': value},
        ) 