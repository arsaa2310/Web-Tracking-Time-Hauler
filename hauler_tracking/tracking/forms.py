from django import forms
from .models import HaulerActivity

class HaulerActivityForm(forms.ModelForm):
    class Meta:
        model = HaulerActivity
        fields = ['hauler', 'driver', 'activity', 'start_time', 'location', 'remarks']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
