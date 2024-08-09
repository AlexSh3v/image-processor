import pprint
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, View


def custom_get_context_data(instance: View, **kwargs):
    context = super(instance.__class__, instance).get_context_data(**kwargs)
    form: UserCreationForm = context['form']
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control' 
    pprint.pprint(form.non_field_errors)
    return context


class MyLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('albums')

    def get_context_data(self, **kwargs):
        return custom_get_context_data(self, **kwargs)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        pprint.pp(form.non_field_errors())
        context['has_error'] = True
        return self.render_to_response(context)


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        return custom_get_context_data(self, **kwargs)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        pprint.pp(form.errors)
        context['has_error'] = True
        return self.render_to_response(context)
    
