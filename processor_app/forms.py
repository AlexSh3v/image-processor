from django import forms
from .models import Images, Albums


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = ['source']

    
class EditImageForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = []
    filter_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    crop_x = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    crop_y = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    crop_width = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    crop_height = forms.IntegerField(widget=forms.HiddenInput(), required=False)


class AlbumEditForm(forms.ModelForm):
    class Meta:
        model = Albums
        fields = ['name']

class AlbumDeleteForm(forms.ModelForm):
    class Meta:
        model = Albums
        fields = []


class DeleteImageForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = []
    is_delete_children = forms.BooleanField(required=False, label='Do you want to delete children also?', initial=False)

