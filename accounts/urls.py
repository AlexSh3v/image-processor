from django.urls import path
from django.contrib.auth import views as auth_views

from accounts.views import MyLoginView, SignUpView

urlpatterns = [
    path('login/', MyLoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
