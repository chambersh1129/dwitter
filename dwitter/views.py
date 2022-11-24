from typing import Any, Dict, Optional, Type

from django.core.paginator import Paginator
from django.db.models import Model, QuerySet
from django.forms import BaseForm, BaseModelForm
from django.http import HttpRequest, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import DweetForm
from .models import Dweet, Profile


class DweetFormMixin(FormMixin):
    """
    Any view that renders templates can add this mixin to add the DweetForm to the context
    """

    def form_valid(self, form: BaseModelForm) -> HttpResponseRedirect:
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super(DweetFormMixin, self).get_context_data(**kwargs)  # type: ignore
        if "dweet_form" not in context:
            context["dweet_form"] = DweetForm
        if "display_dweet_form" not in context:
            context["display_dweet_form"] = True
        return context

    def get_form_class(self) -> Type[BaseForm]:
        return DweetForm

    def get_success_url(self):
        """
        Redirect the user to the page they submitted from
        """
        return self.request.META.get("HTTP_REFERER")


class DashboardView(DweetFormMixin, ListView):
    model: Optional[Type[Model]] = Dweet
    template_name: str = "dwitter/dashboard.html"
    paginate_by: int = 5

    def get_queryset(self) -> QuerySet[Dweet]:
        if self.request.user.is_authenticated:
            follows: list = list(self.request.user.profile.follows.values_list("user", flat=True))
            return Dweet.objects.filter(user__in=follows)  # type: ignore

        return super().get_queryset()  # type: ignore


class DweetCreateView(DweetFormMixin, ProcessFormView):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse("dwitter:dashboard"))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ProfileDetailView(DweetFormMixin, DetailView):
    # DetailView will automagically look for dwitter/templates/dwitter/<model>_detail.html for template
    # username must be unique so we can safely change the slug_field and slug_url_kwarg
    # instead of /profile/1 we can now use /profile/<username>
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"
    paginate_by: int = 5

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        # custom pagination for dweets
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        self.object = self.get_object()
        dweets = Dweet.objects.filter(user=self.object.user)
        paginator = Paginator(dweets, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        context["page_obj"] = paginator.page(page_number)
        context["paginator"] = paginator
        context["display_follow"] = True
        if self.request.user.is_authenticated and self.request.user.profile != self.object:
            context["display_dweet_form"] = False
        return context


class ProfileFollowView(SingleObjectMixin, View):
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
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


class ProfileListView(DweetFormMixin, ListView):
    # ListView will automagically look for dwitter/templates/dwitter/<model>_list.html for template
    model: Optional[Type[Model]] = Profile
    paginate_by: int = 5
