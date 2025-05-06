"""
Storage utilities for the GreenBridge application.
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaS3Boto3Storage(S3Boto3Storage):
    """
    S3 storage backend for media files.
    This separates media from static files for better organization.
    """
    location = 'media'
    file_overwrite = False 