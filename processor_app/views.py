import datetime
import pathlib
from typing import Any
import uuid
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest, Http404
from django.urls import reverse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from image_processor.settings import MEDIA_ROOT
from django.forms.models import model_to_dict
from django.forms import ModelForm

from processor_app.forms import UploadImageForm, EditImageForm, DeleteImageForm, AlbumEditForm, AlbumDeleteForm
from processor_app.models import Images, Albums

from processor_app import proccesor

class PreviewPage(View):
    def get(self, request: HttpRequest, *_, **__):
        return render(request, 'preview.html')


class UploadPage(LoginRequiredMixin, CreateView):
    model = Images
    fields = ['source']
    template_name = 'upload_page.html'

    def form_valid(self, form):
        uploader = self.request.user
        new_album = Albums(
            name=f'Album {form.instance.source.name}',
            uploader=uploader,
        )
        new_album.save()
        form.instance.uploader = uploader
        form.instance.album_id = new_album
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for field in context['form'].fields.values():
            field.widget.attrs['class'] = 'form-control'
        return context
    
    def get_success_url(self) -> str:
        return reverse('image-single', kwargs={'pk': self.object.pk})


class ImageEditView(LoginRequiredMixin, UpdateView):
    model = Images
    form_class = EditImageForm
    template_name = 'edit_image.html'
    
    def get_queryset(self):
        q = Images.objects.filter(uploader=self.request.user)
        return q

    def get_object(self, _=None):
        query = self.get_queryset()
        pk = self.kwargs['pk']
        obj = query.get(pk=uuid.UUID(pk))
        return obj

    def form_valid(self, form):
        filter_type = self.request.POST.get('filter_type')
        crop_x = self.request.POST.get('crop_x')
        crop_y = self.request.POST.get('crop_y')
        crop_width = self.request.POST.get('crop_width')
        crop_height = self.request.POST.get('crop_height')

        img_obj: Images = self.object
        original_path = MEDIA_ROOT / img_obj.source.path
        suffix = original_path.suffix
        print(f'Original Image: {original_path!r}')

        image_pillow_object = proccesor.get_image(original_path)
        image_pillow_object = proccesor.crop(image_pillow_object, crop_x, crop_y, crop_width, crop_height)
        if filter_type not in proccesor.available_types:
            # TODO: show error message, that filter is undefined!
            print(f'[ImageEdit] filter is UNDEFINED: {filter_type!r}')
        elif filter_type != 'none':
            print(f'[ImageEdit] setting new filter: {filter_type!r}')
            image_pillow_object = proccesor.filter_(image_pillow_object, filter_type)

        processed_image_content = proccesor.convert_to_content_file(
            image_pillow_object, suffix,
        )

        # file_name = f'processed/{img_obj.id}_processed.png'
        # path_to_file = default_storage.save(file_name, processed_image_content)
        # img_obj.processed = path_to_file
        # img_obj.save()

        processed_image_obj = Images(
            source=processed_image_content,
            # original_id=img_obj.id,
            uploader=self.request.user,
            album_id=img_obj.album_id,
        )
        # FIXME: change type based on the image!
        processed_image_content.name = f'processed_{processed_image_obj.id}{suffix}'
        processed_image_obj.source = processed_image_content
        processed_image_obj.save()

        # messages.success(self.request, 'Image updated successfully!')
        album = img_obj.album_id
        album.edited_at = datetime.datetime.now()
        album.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('image-single', kwargs={'pk': self.get_object().pk})


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = Images
    template_name = 'delete_image.html'
    form_class = DeleteImageForm
    context_object_name = 'image'

    def get_success_url(self) -> str:
        return reverse('album-single', args=(self.get_object().album_id.pk,))

    def get_queryset(self):
        return Images.objects.filter(uploader=self.request.user)

    def get_object(self, _=None):
        query = self.get_queryset()
        pk_uuid_format = self.kwargs['pk']
        obj = query.get(pk=uuid.UUID(pk_uuid_format))
        print(f'Object? {obj}')
        return obj

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form: DeleteImageForm = context['form']
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-check-input ms-2' 
        return context
    
    def form_valid(self, form: DeleteImageForm):
        print(f'[FORM VALID] cleaned: {form.cleaned_data!r}')
        img_obj = self.get_object()
        original_relative_path = img_obj.source.path
        original_full_path = MEDIA_ROOT / original_relative_path
        print(f'[FORM VALID] unlick origin: {original_full_path!r}')
        original_full_path.unlink(missing_ok=True)
        return super().form_valid(form)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('preview')


class ImagesList(LoginRequiredMixin, ListView):
    model = Images
    template_name = 'images.html'
    context_object_name = 'images'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        d: dict[Images, list[str]] = {}
        for image_obj in context[self.context_object_name]:
            if image_obj.original_id is not None:
                continue
            processed_objects = Images.objects.filter(original_id=image_obj.id)
            d[image_obj] = []
            for processed_obj in processed_objects:
                d[image_obj].append(processed_obj)
        context["images_grouped"] = d
        print(f'[context] {context["images_grouped"]}')
        return context
    
    def get_queryset(self) -> QuerySet:
        return Images.objects.filter(uploader=self.request.user)



class BaseUrlRedirection(View):
    def get(self, request: HttpRequest, *_, **__):
        if request.user.is_authenticated:
            return redirect('albums')
        return redirect('login')
        

class ImageSingle(LoginRequiredMixin, DetailView):
    model = Images
    template_name = 'image_single.html'
    context_object_name = 'image'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        image = context['image']
        uploader = self.request.user
        file_format = pathlib.Path(image.source.path).suffix
        context['file_format'] = file_format.strip('.')
        context['processed_images'] = [
            obj for obj in Images.objects.filter(uploader=uploader, album_id=image.album_id)
            if obj.id != image.id
        ]
        print(f'[IMAGE SINGLE] this object:')
        print(image)
        print(f'[IMAGE SINGLE] processed:')
        print(*context["processed_images"], sep='\n')
        return context
    

class AlbumsView(LoginRequiredMixin, ListView):
    model = Albums
    template_name = 'albums.html'
    context_object_name = 'albums'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        d = {}
        for album in context[self.context_object_name]:
            images = album.album_images.all()
            d[album] = {
                'last_image': images[len(images)-1],
                'album_size': len(images),
            }
        context['my_albums'] = d
        print('[ALBUMS]', d)
        return context
    
    def get_queryset(self) -> QuerySet:
        return Albums.objects.filter(uploader=self.request.user).order_by('-edited_at')


class AlbumEditView(LoginRequiredMixin, UpdateView):
    model = Albums
    form_class = AlbumEditForm
    template_name = 'album_edit.html'
    context_object_name = 'album'
    
    def get_queryset(self):
        return Albums.objects.filter(uploader=self.request.user)

    def get_object(self, _=None):
        query = self.get_queryset()
        pk = self.kwargs['pk']
        obj = query.get(pk=uuid.UUID(pk))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = context['form'].fields
        name_input_field_widget = fields['name'].widget
        name_input_field_widget.attrs['placeholder'] = self.get_object().name
        name_input_field_widget.attrs['class'] = 'form-control'
        return context

    def form_valid(self, form):
        album = self.get_object()
        album.edited_at = datetime.datetime.now()
        album.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('album-single', args=(self.get_object().pk,))


class SingleAlbumView(LoginRequiredMixin, DetailView):
    model = Albums
    template_name = 'album_single.html'
    context_object_name = 'album'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        album = context[self.context_object_name]
        images = album.album_images.all()
        context['images'] = images
        print(f'[ALBUM-SINGLE] object:\n{album}')
        print(f'[ALBUM-SINGLE] images:', *images, sep='\n--> ')
        return context


class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    model = Albums
    template_name = 'album_delete.html'
    form_class = AlbumDeleteForm
    context_object_name = 'album'

    def get_success_url(self) -> str:
        return reverse('albums')

    def get_object(self, _=None):
        query = Albums.objects.filter(uploader=self.request.user)
        pk = uuid.UUID(self.kwargs['pk'])
        album_to_delete = query.get(pk=pk)
        return album_to_delete

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        form: AlbumDeleteForm = context['form']
        album_to_delete = self.get_object()
        context['images'] = album_to_delete.album_images.all()
        context['album_size'] = len(context['images'])
        for field in form.fields.values():
            field.widget.attrs['class'] = 'form-check-input ms-2' 
        return context

    def form_valid(self, form: AlbumDeleteForm):
        album_to_delete = self.get_object()
        count = 0
        for image in album_to_delete.album_images.all():
            path = pathlib.Path(image.source.path)
            path.unlink(missing_ok=True)
            count += 1
        print(f'[ALBUM_DELETE] Deleted {count} images from album {album_to_delete.name!r}')
        return super().form_valid(form)
    
