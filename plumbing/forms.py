from django import forms
from .widgets import PlumbingWidget


class PlumbingField(forms.Field):
    widget = PlumbingWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        return initial

    def _has_changed(self, initial, data):
        return False
