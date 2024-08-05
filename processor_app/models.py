import uuid
from django.db import models


class Image(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        # FIXME: turn to False!
        editable=True,
    )
    original = models.ImageField(upload_to='uploads/')
    processed = models.ImageField(upload_to='processed/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    uploader = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Image(id={self.pk}; name={self.original.name!r})'


class ProcessedImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    original = models.ForeignKey(
        Image, on_delete=models.CASCADE,
    )
    processed = models.ImageField(upload_to='processed/')
    edited_at = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'ProcessedImage(id={self.pk}; name={self.processed.name!r})'
