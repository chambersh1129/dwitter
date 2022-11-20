from typing import Optional, Type

from django.db.models import Model, QuerySet
from django.views.generic import DetailView, ListView, TemplateView

from .models import Profile


# Create your views here.
class Dashboard(TemplateView):
    template_name: str = "base.html"


class ProfileDetail(DetailView):
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"


class ProfileList(ListView):
    model: Optional[Type[Model]] = Profile

    def get_queryset(self) -> QuerySet[Profile]:
        return super().get_queryset().exclude(user=self.request.user)  # type: ignore
