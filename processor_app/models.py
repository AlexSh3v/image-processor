import uuid
from django.db import models


class Albums(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(max_length=256, default='Image')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    uploader = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return f'Album(id={self.id}; name={self.name!r})'
    

class Images(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        # FIXME: turn to False!
        editable=True,
    )
    name = models.CharField(max_length=256, default='Image')
    album_id = models.ForeignKey(
        Albums, 
        on_delete=models.CASCADE,
        related_name='album_images',
        null=True, blank=True,
    )
    source = models.ImageField(upload_to='uploads/')
    original_id = models.UUIDField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    uploader = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'Image(id={self.pk}; name={self.source.name!r})'

