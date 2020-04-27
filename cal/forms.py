from django.forms import ModelForm, DateInput, TimeInput, HiddenInput
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from cal.models import Event, Metadata
from datetime import datetime, date, time

class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_date': DateInput(attrs={'type':'date'}),
            'end_date': DateInput(attrs={'type':'date'}),
            'start_hm': TimeInput(attrs={'type':'time'}, format='%H:%M'),
            'end_hm': TimeInput(attrs={'type':'time'}, format='%H:%M'),
        }
        exclude = ['start_time', 'end_time', 'user']
        labels = {
            'start_hm':('Start time'),
            'end_hm':('End time'),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(EventForm, self).__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        # Saves the event, filling in start_time and end_time using the separate date and time (hm) fields.
        form = super(EventForm, self).save(commit=False)
        start_time = get_datetime(self.cleaned_data['start_date'], self.cleaned_data['start_hm'])
        end_time = get_datetime(self.cleaned_data['end_date'], self.cleaned_data['end_hm'])
        form.start_time = start_time
        form.end_time = end_time
        form.user = self.user
        if commit:
            form.save()
        return form

def get_datetime(d, hm):
    if d and hm:
        return datetime.combine(d, hm)
    elif d:
        return datetime.combine(d, time(0, 0, 0))
    return None