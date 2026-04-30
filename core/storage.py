import os

from cloudinary_storage.storage import MediaCloudinaryStorage, RESOURCE_TYPES


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
