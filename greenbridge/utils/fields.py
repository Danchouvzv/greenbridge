"""
Custom model fields for the GreenBridge application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class UUIDField(models.UUIDField):
    """
    Custom UUID field with default as uuid4.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('editable', False)
        kwargs.setdefault('unique', True)
        super().__init__(*args, **kwargs)


class PercentageField(models.FloatField):
    """
    Custom percentage field (0-100).
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('validators', [
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ])
        kwargs.setdefault('help_text', 'Value must be between 0 and 100')
        super().__init__(*args, **kwargs)


class WeightField(models.DecimalField):
    """
    Custom weight field in kilograms.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 10)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('validators', [MinValueValidator(0.0)])
        kwargs.setdefault('help_text', 'Weight in kilograms')
        super().__init__(*args, **kwargs)


class MoneyField(models.DecimalField):
    """
    Custom money field.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_digits', 14)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('validators', [MinValueValidator(0.0)])
        kwargs.setdefault('help_text', 'Amount in default currency')
        super().__init__(*args, **kwargs)


class EncryptedTextField(models.TextField):
    """
    Field for storing encrypted text.
    
    Note: This is a placeholder. In a real implementation,
    this would include encryption/decryption methods.
    """
    description = "Encrypted text field"
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('help_text', 'This field is stored encrypted')
        super().__init__(*args, **kwargs)
    
    # In a real implementation, you would override get_prep_value and from_db_value
    # to handle encryption and decryption 