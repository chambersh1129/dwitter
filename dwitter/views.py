from typing import Any, Dict, Optional, Type

from django.db.models import Model, QuerySet
from django.forms import BaseForm, BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import DweetForm
from .models import Dweet, Profile


class DweetFormMixin:
    """
    Any view that renders templates can add this mixin to add the DweetForm to the context
    """

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context["dweet_form"] = DweetForm
        return context


class DashboardView(DweetFormMixin, ListView):
    model: Optional[Type[Model]] = Dweet
    template_name: str = "dwitter/dashboard.html"

    def get_queryset(self) -> QuerySet[Dweet]:
        if self.request.user.is_authenticated:
            follows: list = list(self.request.user.profile.follows.values_list("user", flat=True))
            return Dweet.objects.filter(user__in=follows)  # type: ignore

        return super().get_queryset()  # type: ignore


class DweetCreateView(DweetFormMixin, CreateView):
    model: Optional[Type[Model]] = Dweet
    form_class: Optional[Type[BaseForm]] = DweetForm

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """
        Redirect the user to the page they submitted from
        """
        return self.request.META.get("HTTP_REFERER")


class ProfileDetailView(DweetFormMixin, DetailView):
    # DetailView will automagically look for dwitter/templates/dwitter/<model>_detail.html for template
    # username must be unique so we can safely change the slug_field and slug_url_kwarg
    # instead of /profile/1 we can now use /profile/<username>
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"


class ProfileFollowView(SingleObjectMixin, View):
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"

    def post(self, request: HttpRequest, *args, **kwargs):
        # AnonymousUser cannot follow anyone
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object = self.get_object()
        current_user_profile = request.user.profile

        # Users cannot follow/unfollow themselves
        if self.object != current_user_profile:
            action = request.POST.get("follow")
            if action == "follow":
                current_user_profile.follows.add(self.object)
            elif action == "unfollow":
                current_user_profile.follows.remove(self.object)
            current_user_profile.save()

        return HttpResponseRedirect(reverse("dwitter:profile-detail", kwargs={"username": self.object.user.username}))


class ProfileListView(ListView):
    # ListView will automagically look for dwitter/templates/dwitter/<model>_list.html for template
    model: Optional[Type[Model]] = Profile

    def get_queryset(self) -> QuerySet[Profile]:
        if self.request.user.is_authenticated:
            return super().get_queryset().exclude(user=self.request.user)  # type: ignore

        return super().get_queryset()  # type: ignore
