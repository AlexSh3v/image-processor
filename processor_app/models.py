import uuid
from django.db import models


class Images(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        # FIXME: turn to False!
        editable=True,
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

