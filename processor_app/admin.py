from django.contrib import admin

from .models import Image, ProcessedImage


admin.site.register(Image)
admin.site.register(ProcessedImage)
