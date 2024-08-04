import uuid
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, UpdateView, DeleteView, ListView
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from image_processor.settings import MEDIA_ROOT

from processor_app.forms import UploadImageForm, EditImageForm
from processor_app.models import Image

from processor_app import proccesor

class PreviewPage(View):
    def get(self, request: HttpRequest, *_, **__):
        return render(request, 'preview.html')


class UploadPage(LoginRequiredMixin, View):
    # login_url = '/accounts/login/'
    # redirect_field_name = '/upload/'

    def get(self, request: HttpRequest):
        form = UploadImageForm()
        context = {'form': form, }
        return render(request, 'upload_page.html', context)

    def post(self, request: HttpRequest):
        request.user: User
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
        # pk = self.kwargs['pk']
        # pk = uuid.UUID(self.kwargs['pk'])
        # for obj in q:
            
        #     print('=============================================================')
        #     print(repr(pk))
        #     print(repr(obj.pk))
        #     print(pk == obj.pk)
        #     print('=============================================================')
        print(f'set is {q}')
        return q

    def get_object(self, _=None):
        print('LOL===============================================')
        query = self.get_queryset()
        pk = self.kwargs['pk']
        obj = query.get(pk=uuid.UUID(pk))
        print(f'found object!: {obj}')
        print('===============================================')
        return obj

    def form_valid(self, form):
        print('form is valid!!!')
        crop_x = self.request.POST.get('crop_x')
        crop_y = self.request.POST.get('crop_y')
        crop_width = self.request.POST.get('crop_width')
        crop_height = self.request.POST.get('crop_height')
        print('VALUES!:', crop_x, crop_y, crop_width, crop_height)

        img: Image = self.object
        original_path = MEDIA_ROOT / img.original.path

        #################################################
        # with original_path.open('rb') as origin:
        #     copied = MEDIA_ROOT / 'copied.png'
        #     with copied.open('wb') as cp:
        #         cp.write(origin.read())
        #################################################

        processed_image_content = proccesor.crop(original_path, crop_x, crop_y, crop_width, crop_height)
        file_name = f'processed/{img.id}_processed.png'
        path_to_file = default_storage.save(file_name, processed_image_content)

        img.processed = path_to_file
        img.save()

        messages.success(self.request, 'Image updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('images')


class ImageDeleteView(LoginRequiredMixin, DeleteView):
    model = Image
    template_name = 'confirm_delete.html'  # Создайте этот шаблон для подтверждения удаления
    success_url = reverse_lazy('my_images')  # Замените на ваш URL для отображения изображений

    def get_queryset(self):
        return Image.objects.filter(uploader=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Image deleted successfully!')
        return super().delete(request, *args, **kwargs)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('preview')


class ImagesList(LoginRequiredMixin, ListView):
    model = Image
    template_name = 'images.html'
    context_object_name = 'images'

