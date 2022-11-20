from django.views.generic import TemplateView


# Create your views here.
class dashboard(TemplateView):
    template_name: str = "base.html"
