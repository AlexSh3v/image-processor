from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from processor_app import views

urlpatterns = [
    path('preview/', views.PreviewPage.as_view(), name='preview'),
    path('upload/', views.UploadPage.as_view(), name='upload'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
