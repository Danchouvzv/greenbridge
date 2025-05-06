"""
API views for the Accounts app.
"""
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.exceptions import ValidationError

from greenbridge.utils.permissions import IsOwner, IsAdminOrReadOnly
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, UserLoginSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users.
    
    Provides CRUD operations with proper permissions.
    Includes actions for password change and profile management.
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Set custom permissions for different actions."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        elif self.action == 'list':
            return [permissions.IsAdminUser()]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Change password for a user.
        
        Requires current password and new password (with confirmation).
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response(
                    {'current_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API endpoint for user login.
    
    Returns JWT tokens upon successful authentication.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Handle user login.
        
        Returns JWT tokens if credentials are valid.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(email=email, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API endpoint to request a password reset.
    
    Generates a token and sends a reset email.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Handle password reset request.
        
        Sends a reset email with token if user exists.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                # Generate token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # In a real app, send an email with the reset link
                # For now, just return the token and uid
                return Response({
                    'message': 'Password reset email sent',
                    'data': {
                        'uid': uid,
                        'token': token
                    }
                }, status=status.HTTP_200_OK)
            
            except User.DoesNotExist:
                # Return success even if user doesn't exist for security
                return Response(
                    {'message': 'Password reset email sent if user exists'},
                    status=status.HTTP_200_OK
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API endpoint to confirm a password reset.
    
    Validates token and sets new password.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Handle password reset confirmation.
        
        Sets new password if token is valid.
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid)
                
                # Validate token
                if default_token_generator.check_token(user, serializer.validated_data['token']):
                    # Set new password
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response(
                        {'message': 'Password has been reset successfully'},
                        status=status.HTTP_200_OK
                    )
                
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
                return Response(
                    {'error': 'Invalid reset link'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating the authenticated user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return the authenticated user."""
        return self.request.user 