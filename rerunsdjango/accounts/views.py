# Taken from https://learndjango.com/tutorials/django-signup-tutorial
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views import generic
from .models import CustomUser
from .forms import CustomUserCreationForm


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

class UserListView(generic.ListView):
    model = CustomUser
    template_name = 'accounts/users_list.html'
    context_object_name = 'users_list'

class UserProfileDetailView(generic.DetailView):
    model = CustomUser
    template_name = 'accounts/detail.html'
    fields = [
        "username", "timezone"
    ]

class UserProfileUpdateView(PermissionRequiredMixin, generic.UpdateView):
    permission_required = "accounts.update_customuser"
    model = CustomUser
    fields = [
        "timezone"
    ]