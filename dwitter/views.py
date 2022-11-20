from typing import Optional, Type

from django.db.models import Model, QuerySet
from django.views.generic import DetailView, ListView, TemplateView

from .models import Profile


# Create your views here.
class DashboardView(TemplateView):
    template_name: str = "base.html"


class ProfileDetailView(DetailView):
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"


class ProfileListView(ListView):
    model: Optional[Type[Model]] = Profile

    def get_queryset(self) -> QuerySet[Profile]:
        if self.request.user.is_authenticated:
            return super().get_queryset().exclude(user=self.request.user)  # type: ignore

        return super().get_queryset()  # type: ignore
