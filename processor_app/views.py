import textwrap
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
from django.views.generic import View, UpdateView, DeleteView, ListView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from image_processor.settings import MEDIA_ROOT

from processor_app.forms import UploadImageForm, EditImageForm
from processor_app.models import Image, ProcessedImage

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
    model = Image
    form_class = EditImageForm
    template_name = 'edit_image.html'
    
    def get_queryset(self):
        q = Image.objects.filter(uploader=self.request.user)
        return q

    def get_object(self, _=None):
        query = self.get_queryset()
        pk = self.kwargs['pk']
        obj = query.get(pk=uuid.UUID(pk))
        return obj

    def form_valid(self, form):
        crop_x = self.request.POST.get('crop_x')
        crop_y = self.request.POST.get('crop_y')
        crop_width = self.request.POST.get('crop_width')
        crop_height = self.request.POST.get('crop_height')

        img_obj: Image = self.object
        original_path = MEDIA_ROOT / img_obj.original.path
        processed_image_content = proccesor.crop(original_path, crop_x, crop_y, crop_width, crop_height)

        # file_name = f'processed/{img_obj.id}_processed.png'
        # path_to_file = default_storage.save(file_name, processed_image_content)
        # img_obj.processed = path_to_file
        # img_obj.save()

        processed_image = ProcessedImage(
            original=img_obj,
            processed=processed_image_content,
            uploader=self.request.user,
        )
        processed_image.save()

        messages.success(self.request, 'Image updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('images')


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = Image
    template_name = 'delete_image.html'
    success_url = reverse_lazy('images')

    def get_queryset(self):
        return Image.objects.filter(uploader=self.request.user)

    def get_object(self, _=None):
        query = self.get_queryset()
        pk_uuid_format = self.kwargs['pk']
        obj = query.get(pk=uuid.UUID(pk_uuid_format))
        return obj

    def post(self, request, *args, **kwargs):
        img_obj = self.get_object()
        original_relative_path = img_obj.original.path
        original_full_path = MEDIA_ROOT / original_relative_path
        print(f'[delete] unlick origin: {original_full_path!r}')
        original_full_path.unlink(missing_ok=True)
        queryset = Image.objects.filter(original=original_relative_path)
        print(f'[delete] should be empty: {queryset}', sep='\n')
        for it in ProcessedImage.objects.filter(original=img_obj.id):
            processed_path = MEDIA_ROOT / it.processed.path
            print(f'  [delete] unlink: {processed_path!r}')
            processed_path.unlink(missing_ok=True)
        return super().post(request, *args, **kwargs)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('preview')


class ImagesList(LoginRequiredMixin, ListView):
    model = Image
    template_name = 'images.html'
    context_object_name = 'images'
    
    def get_queryset(self) -> QuerySet:
        return Image.objects.filter(uploader=self.request.user)



class BaseUrlRedirection(View):
    def get(self, request: HttpRequest, *_, **__):
        if request.user.is_authenticated:
            return redirect('images')
        return redirect('login')
        
