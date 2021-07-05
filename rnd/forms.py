from django import forms
from .models import Category, BaseAdvertise


class AdvertiseForm(forms.ModelForm):

    class Meta:
        model = BaseAdvertise
        exclude = ('user', 'category', 'availability', 'content_type', 'object_id')
