"""
Custom exception handling for the GreenBridge API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    Standardizes error responses across the API.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # If response is None, there was an unhandled exception
    if response is None:
        return Response({
            'error': True,
            'message': 'Internal server error',
            'details': str(exc) if hasattr(exc, '__str__') else 'Unknown error',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Add error flag to all error responses
    if not hasattr(response, 'data') or not isinstance(response.data, dict):
        response.data = {'error': True, 'message': 'Error occurred', 'details': response.data}
    else:
        # Format the existing error data
        error_data = {
            'error': True,
        }
        
        # Add message if available
        if 'detail' in response.data:
            error_data['message'] = response.data.pop('detail')
        else:
            error_data['message'] = 'Error occurred'
            
        # Keep all other error details
        error_data['details'] = response.data
        
        response.data = error_data

    return response 