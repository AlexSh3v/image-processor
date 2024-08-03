from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpRequest, Http404
from django.shortcuts import render, redirect
from django.views.generic import View, CreateView

from processor_app.forms import UploadImageForm
from processor_app.models import Image


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


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('preview')


@login_required
def images_view(request: HttpRequest):
    if request.method != 'GET':
        return Http404()

    print(request.user.id)
    images = Image.objects.filter(uploader=request.user)
    img = images[0]
    print(f'Image? {images}')
    context = {'images': images, }
    return render(request, 'images.html', context)
