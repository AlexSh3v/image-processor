from django.db import models


class Image(models.Model):
    original = models.ImageField(upload_to='uploads/')
    processed = models.ImageField(upload_to='processed/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Image(id={self.pk})'
