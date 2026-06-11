import os

from cloudinary_storage.storage import MediaCloudinaryStorage, RESOURCE_TYPES

try:
    from storages.backends.gcloud import GoogleCloudStorage
    from google.cloud.exceptions import NotFound
    HAS_DJANGO_STORAGES = True
except ImportError:
    GoogleCloudStorage = object
    HAS_DJANGO_STORAGES = False

    class NotFound(Exception):
        pass


class MixedMediaCloudinaryStorage(MediaCloudinaryStorage):
    image_extensions = {'.avif', '.gif', '.jpeg', '.jpg', '.png', '.svg', '.webp'}
    video_extensions = {'.avi', '.m4v', '.mov', '.mp4', '.mpeg', '.mpg', '.webm'}

    def _get_resource_type(self, name):
        extension = os.path.splitext(name or '')[1].lower()
        if extension in self.image_extensions:
            return RESOURCE_TYPES['IMAGE']
        if extension in self.video_extensions:
            return RESOURCE_TYPES['VIDEO']
        return RESOURCE_TYPES['RAW']


class SafeGoogleCloudStorage(GoogleCloudStorage):
    """
    Wrapper around GoogleCloudStorage that handles missing files gracefully.
    When a file doesn't exist in the bucket, methods like size() and
    get_modified_time() return None instead of raising NotFound exceptions.
    This prevents errors when Django's FileField tries to delete old files
    that don't exist in Google Cloud Storage.
    """

    def __init__(self, *args, **kwargs):
        if not HAS_DJANGO_STORAGES:
            raise ImportError("django-storages is required when USE_GCS=true")
        super().__init__(*args, **kwargs)

    def size(self, name):
        try:
            return super().size(name)
        except NotFound:
            return 0

    def get_modified_time(self, name):
        try:
            return super().get_modified_time(name)
        except NotFound:
            return None

    def get_created_time(self, name):
        try:
            return super().get_created_time(name)
        except NotFound:
            return None
