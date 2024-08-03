from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View

from processor_app.forms import UploadImageForm


class PreviewPage(View):
    def get(self, request: HttpRequest, *_, **__):
        return render(request, 'preview.html')


class UploadPage(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = '/upload/'

    def get(self, request: HttpRequest, *_, **__):
        form = UploadImageForm()
        context = {
            'form': form,
        }
        return render(request, 'upload_page.html', context)

    def post(self, request: HttpRequest, *_, **__):
        print('request POST!')
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload')
        print('gone wild ...')
        # context = {
        #     'form': form,
        # }
        # return render(request, 'upload_page.html', context)


def logout_view(request: HttpRequest):
    logout(request)
    return redirect('preview')
