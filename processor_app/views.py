from typing import Any
import uuid
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.http import HttpRequest, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView, DeleteView, ListView, DetailView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from image_processor.settings import MEDIA_ROOT
from django.forms.models import model_to_dict

from processor_app.forms import UploadImageForm, EditImageForm, DeleteImageForm
from processor_app.models import Images

from processor_app import proccesor

class PreviewPage(View):
    def get(self, request: HttpRequest, *_, **__):
        return render(request, 'preview.html')


class UploadPage(LoginRequiredMixin, View):
    def get(self, request: HttpRequest):
        form = UploadImageForm()
        context = {'form': form, }
        return render(request, 'upload_page.html', context)

    def post(self, request: HttpRequest):
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.uploader = request.user
            image.save()
            print('saved!')
            return redirect('images')
        print('skip!')
        print('errors:', form.errors)
        return render(request, 'upload_page.html', {'form': form})


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
        print(f'Original Image: {original_path!r}')
        processed_image_content = proccesor.crop(original_path, crop_x, crop_y, crop_width, crop_height)

        if filter_type not in proccesor.available_types:
            # TODO: show error message, that filter is undefined!
            print(f'[ImageEdit] filter is UNDEFINED: {filter_type!r}')
            ...
        elif filter_type != 'none':
            print(f'[ImageEdit] setting new filter: {filter_type!r}')
            processed_image_content = proccesor.filter_(processed_image_content, filter_type)

        # file_name = f'processed/{img_obj.id}_processed.png'
        # path_to_file = default_storage.save(file_name, processed_image_content)
        # img_obj.processed = path_to_file
        # img_obj.save()

        processed_image_obj = Images(
            source=processed_image_content,
            original_id=img_obj.id,
            uploader=self.request.user,
        )
        # FIXME: change type based on the image!
        processed_image_content.name = f'processed_{processed_image_obj.id}.png'
        processed_image_obj.source = processed_image_content
        processed_image_obj.save()

        messages.success(self.request, 'Image updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('images')


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = Images
    template_name = 'delete_image.html'
    form_class = DeleteImageForm
    success_url = reverse_lazy('images')
    context_object_name = 'image'

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
        print(f'CONTEXT!! {context}')
        return context
    

    def post(self, request, *args, **kwargs):
        print(f'POST!: {self.request.POST}')
        delete_children_check = self.request.POST.get('is_delete_children')
        img_obj = self.get_object()
        original_relative_path = img_obj.source.path
        original_full_path = MEDIA_ROOT / original_relative_path
        print(f'[delete] unlick origin: {original_full_path!r}')
        original_full_path.unlink(missing_ok=True)
        queryset = Images.objects.filter(source=original_relative_path)
        print(f'[delete] should be empty: {queryset}', sep='\n')
        for it in Images.objects.filter(original_id=img_obj.id):
            if not delete_children_check:
                break
            processed_path = MEDIA_ROOT / it.source.path
            print(f'  [delete] unlink: {processed_path!r}')
            processed_path.unlink(missing_ok=True)
            it.delete()
        return super().post(request, *args, **kwargs)


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
            return redirect('images')
        return redirect('login')
        

class ImageSingle(LoginRequiredMixin, DetailView):
    model = Images
    template_name = 'image_single.html'
    context_object_name = 'image'
