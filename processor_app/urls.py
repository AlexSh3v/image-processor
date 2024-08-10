from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from processor_app import views

urlpatterns = [
    # Common
    path('', views.BaseUrlRedirection.as_view(), name='base-redirection'),
    path('preview/', views.PreviewPage.as_view(), name='preview'),
    path('upload/', views.UploadPage.as_view(), name='upload'),
    
    # Images
    # path('images/', views.ImagesList.as_view(), name='images'),
    path('image/<str:pk>', views.ImageSingle.as_view(), name='image-single'),
    path('edit/<str:pk>', views.ImageEditView.as_view(), name='edit'),
    path('delete/<str:pk>', views.ImageDeleteView.as_view(), name='image-delete'),

    # Albums
    path('albums/', views.AlbumsView.as_view(), name='albums'),
    path('album/<str:pk>', views.SingleAlbumView.as_view(), name='album-single'),
    path('album/edit/<str:pk>', views.AlbumEditView.as_view(), name='album-edit'),
    path('album/delete/<str:pk>', views.AlbumDeleteView.as_view(), name='album-delete'),
]
