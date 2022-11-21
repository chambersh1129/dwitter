from typing import Optional, Type

from django.db.models import Model, QuerySet
from django.views.generic import DetailView, ListView

from .models import Dweet, Profile


class DashboardView(ListView):
    model: Optional[Type[Model]] = Dweet
    template_name: str = "dwitter/dashboard.html"

    def get_queryset(self) -> QuerySet[Dweet]:
        if self.request.user.is_authenticated:
            follows: list = list(self.request.user.profile.follows.values_list("user", flat=True))
            return Dweet.objects.filter(user__in=follows)  # type: ignore

        return super().get_queryset()  # type: ignore


class ProfileDetailView(DetailView):
    # DetailView will automagically look for dwitter/templates/dwitter/<model>_detail.html for template
    # username must be unique so we can safely change the slug_field and slug_url_kwarg
    # instead of /profile/1 we can now use /profile/<username>
    model: Type[Model] = Profile
    slug_field: str = "user__username"
    slug_url_kwarg: str = "username"

    def post(self, request, *args, **kwargs):
        # Users should not be able to follow/unfollow themselves so make sure
        self.object = self.get_object()
        current_user_profile = request.user.profile

        if self.object != current_user_profile:
            action = request.POST.get("follow")
            if action == "follow":
                current_user_profile.follows.add(self.object)
            elif action == "unfollow":
                current_user_profile.follows.remove(self.object)
            current_user_profile.save()

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ProfileListView(ListView):
    # ListView will automagically look for dwitter/templates/dwitter/<model>_list.html for template
    model: Optional[Type[Model]] = Profile

    def get_queryset(self) -> QuerySet[Profile]:
        if self.request.user.is_authenticated:
            return super().get_queryset().exclude(user=self.request.user)  # type: ignore

        return super().get_queryset()  # type: ignore
