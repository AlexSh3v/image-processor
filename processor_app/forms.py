from django import forms
from .models import Image


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['original']

    
class EditImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = []
    filter_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    crop_x = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    crop_y = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    crop_width = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    crop_height = forms.IntegerField(widget=forms.HiddenInput(), required=False)
