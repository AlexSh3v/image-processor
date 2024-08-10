from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm


# class EditImageForm(forms.ModelForm):
#     class Meta:
#         model = Images
#         fields = []
#     filter_type = forms.CharField(widget=forms.HiddenInput(), required=False)
#     crop_x = forms.IntegerField(widget=forms.HiddenInput(), required=False)


# class SignUpForm(UserCreationForm):

#     def __init__(self, *args: Any, **kwargs: Any) -> None:
#         super().__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({'class': ''})
#         print(self.form)
#         """
#         self.fields['myfield'].widget.attrs.update({'class': 'myfieldclass'})
#         {'username': <django.contrib.auth.forms.UsernameField object at 0x000002491FDB69D0>, 
#         'password1': <django.forms.fields.CharField object at 0x000002491FDB6B10>
#         'password2': <django.forms.fields.CharField object at 0x000002491FDB6C50>}
#         """
