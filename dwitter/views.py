"""Views for the "dwitter" application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/ref/views/
"""
from django.db.models import Model
from django.views.generic import ListView, TemplateView

from .models import Dweet, Profile


class HomeView(TemplateView):
    template_name: str = "dwitter/home.html"


class DweetListView(ListView):
    model: Model = Dweet
    paginate_by: int = 10


class ProfileListView(ListView):
    model: Model = Profile
    paginate_by: int = 10
