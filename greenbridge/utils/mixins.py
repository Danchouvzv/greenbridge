"""
Model and view mixins for the GreenBridge application.
"""
from django.db import models
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides timestamp fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    An abstract base model that provides soft deletion.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Override delete method to provide soft deletion."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete the object."""
        return super().delete(using=using, keep_parents=keep_parents)


class AuditableModel(models.Model):
    """
    An abstract base model that provides audit fields.
    """
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class OwnedModel(models.Model):
    """
    An abstract base model that establishes ownership with a ForeignKey.
    """
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name="%(class)s_owned")

    class Meta:
        abstract = True


class CreateModelMixin:
    """
    Mixin for handling create operations in API views with custom response.
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': f"{self.serializer_class.Meta.model.__name__} created successfully",
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class UpdateModelMixin:
    """
    Mixin for handling update operations in API views with custom response.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': f"{self.serializer_class.Meta.model.__name__} updated successfully",
            'data': serializer.data
        }) 