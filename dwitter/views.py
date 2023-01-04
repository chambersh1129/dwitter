"""Views for the "dwitter" application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/ref/views/
"""
import json
from typing import Any, Dict, Optional, Type

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Model, QuerySet
from django.forms import BaseForm, BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import DweetForm
from .models import Dweet, Profile


class DweetFormMixin(FormMixin):
    """Mixin to add scaffolding to render, submit, and validate DweetForm.

    Args:
        FormMixin (FormMixin): minimum mixin to handle forms

    """

    request: HttpRequest

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """Create the Dweet based on validated form data.

        Args:
            form (q): pre-validated DeetForm

        Returns
            HttpResponse: calls super, which should eventually call get_success_url() below

        """
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add custom context data to render form.

        Context
            dweet_form (Form): DweetForm object, named so as to not overwrite default form in view
            display_dweet_form (boolean): signal to template engine to render the form

        Returns
            Dict[str, Any]: existing context dictionary, plus information related to DweetForm

        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)  # type: ignore
        context["dweet_form"] = DweetForm
        context["display_dweet_form"] = True
        return context

    def get_form_class(self) -> Type[BaseForm]:
        """Instead of setting the class variable we overwrite the get_form_class to always return DweetForm.

        Returns
            Type[BaseForm]: DweetForm

        """
        return DweetForm

    def get_success_url(self) -> str:
        """Redirect the user to the page they submitted from for fallback to the dashboard.

        Returns
            str: prefer HTTP_REFERER header, dashboard view as a fallback

        """
        return self.request.META.get("HTTP_REFERER") or reverse("dwitter:dashboard")

    def form_invalid(self, form: BaseModelForm) -> HttpResponseRedirect:
        """Dweetform is invalid for some reason, try to get the info and add a message for the user.

        Args:
            form (BaseModelForm): Dweet form

        Returns
            HttpResponseRedirect: Redirect to the same place a successful submission would, just with error context

        """
        error_dict = json.loads(form.errors.as_json())
        if "body" in error_dict:
            errors = []
            for error in error_dict["body"]:
                errors.append(f"{error['message']}")
            messages.error(self.request, "\n".join(errors))

        else:
            messages.error(self.request, "Dweet cannot be empty")

        return HttpResponseRedirect(self.get_success_url())


class DashboardView(DweetFormMixin, ListView):
    """Render the homepage with a paginated list of Dweets.

    Args:
        DweetFormMixin (FormMixin): Mixin to render/submit DweetForm
        ListView (_type_): List Dweet objects

    """

    model: Optional[Type[Model]] = Dweet
    template_name: str = "dwitter/dashboard.html"
    paginate_by: int = 5

    def get_queryset(self) -> QuerySet[Dweet]:
        """Overwrite method to only show Dweets of profiles the logged in user follows.

        Returns
            QuerySet[Dweet]: List of Dweet objects

        """
        if self.request.user.is_authenticated:
            follows: list[Profile] = list(
                self.request.user.profile.follows.values_list("user", flat=True)  # type: ignore
            )
            return Dweet.objects.filter(user__in=follows)

        return super().get_queryset()  # type: ignore


class DweetCreateView(DweetFormMixin, ProcessFormView):
    """Create a Dweet model instance.

    Args:
        DweetFormMixin (Form): Adds methods to handle the Dweet Model Form
        ProcessFormView (View): Remainder of the plumbing to validate the Form and create Dweet model

    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Redirect user to the Dashboard.

        Args:
            request (HttpRequest):

        Returns
            HttpResponseRedirect: Redirecto to the Dashbaord
        """
        return HttpResponseRedirect(reverse("dwitter:dashboard"))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Create a Dweet model instance based on submitted form data.

        Args:
            request (HttpRequest): POST data should be received from the DweetForm submission

        Returns
            HttpResponse: Could either return a 403 Forbidden or 302 Redirect
        """
        # AnonymousUser cannot dweet
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)


class ProfileDetailView(DweetFormMixin, DetailView):
    """Render a single instace of User/Profile model.

    Args:
        DweetFormMixin (Form): Adds methods to handle the Dweet Model Form
        DetailView (View): Adds remaining methods to render a single instance of Profile

    DetailView will automagically look for dwitter/templates/dwitter/<model>_detail.html for template
    username must be unique so we can safely change the slug_field and slug_url_kwarg

    Example:
        instead of /profile/1 we can now use /profile/<username>
    """

    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"
    paginate_by: int = 5
    object: Profile

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Adds custom pagination for dweets.

        Returns
            Dict[str, Any]: context dictionary referenced when rendering a Django template
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        self.object: Profile = self.get_object()
        dweets: QuerySet = Dweet.objects.filter(user=self.object.user)
        paginator = Paginator(dweets, self.paginate_by)
        page_number: int = int(self.request.GET.get("page", 1))
        context["page_obj"] = paginator.page(page_number)
        context["paginator"] = paginator
        context["display_follow"] = True
        return context


class ProfileFollowView(SingleObjectMixin, View):
    """Allow the logged in user to follow/unfollow a User/Profile.

    Args:
        SingleObjectMixin (View): Methods to retrieve/rendoer a single instance of a Model
        View (View): Adds remaining methods to render the view

    """

    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"
    object: Profile

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """Redirect user to the User/Profile detail page.

        Args:
            request (HttpRequest): Request path will contain username of who they attempted to follow/unfollow

        Returns
            HttpResponseRedirect: Redirecto to the Profile of the username in the URL path
        """
        self.object: Profile = self.get_object()
        return HttpResponseRedirect(reverse("dwitter:profile-detail", kwargs={"username": self.object.user.username}))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Allow the following/unfollowing of a User/Profile.

        Args:
            request (HttpRequest): POST data should be received from the DweetForm submission

        Returns
            HttpResponse: Could either return a 403 Forbidden or 302 Redirect
        """
        # AnonymousUser cannot follow anyone
        if not request.user.is_authenticated:
            return HttpResponseForbidden()

        self.object: Profile = self.get_object()
        current_user_profile: Profile = request.user.profile  # type: ignore

        # Users cannot follow/unfollow themselves
        if self.object != current_user_profile:
            action: Optional[str] = request.POST.get("follow")
            if action == "follow":
                current_user_profile.follows.add(self.object)
            elif action == "unfollow":
                current_user_profile.follows.remove(self.object)
            current_user_profile.save()

        return HttpResponseRedirect(reverse("dwitter:profile-detail", kwargs={"username": self.object.user.username}))


class ProfileListView(DweetFormMixin, ListView):
    """List all profiles and allow the submission of a Dweet Form.

    Args:
        DweetFormMixin (Form): Adds methods to handle the Dweet Model Form
        ListView (View): Adds remaining methods to render a list of Profiles

    ListView will automagically look for dwitter/templates/dwitter/<model>_list.html for template
    """

    model: Optional[Type[Model]] = Profile
    paginate_by: int = 5
