"""
Custom permissions for the GreenBridge API.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    message = "You must be the owner of this object to perform this action."
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has an owner attribute
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Check if the object is the user
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
            
        return False


class IsRecycler(permissions.BasePermission):
    """
    Permission to only allow users with recycler role.
    """
    message = "You must be a recycler to perform this action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'recycler'


class IsBrand(permissions.BasePermission):
    """
    Permission to only allow users with brand role.
    """
    message = "You must be a brand to perform this action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'brand'


class IsCharity(permissions.BasePermission):
    """
    Permission to only allow users with charity role.
    """
    message = "You must be a charity to perform this action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'charity'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow admins to edit but allow anyone to read.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admins
        return request.user and request.user.is_staff


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission to only allow verified users.
    """
    message = "Your account must be verified to perform this action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified 