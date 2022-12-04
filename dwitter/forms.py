"""Forms for the "dwitter" application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/forms/
"""
from django import forms

from .models import Dweet


class DweetForm(forms.ModelForm):
    """Form for the "Dweet" model.

    Args:
        forms (ModelForm): use the Django ModelForm to help auto-determine fields

    """

    body = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={"placeholder": "Dweet something...", "class": "textarea is-success is-medium", "rows": 5}
        ),
        label="",
    )

    class Meta:
        """Ties the Form to the "Dweet" model and prevents the submitter from modifying the "user" field."""

        model = Dweet
        fields = ["body"]
