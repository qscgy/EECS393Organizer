from django.forms import ModelForm, DateInput, TimeInput, HiddenInput
from cal.models import Event
from datetime import datetime, date

class EventForm(ModelForm):
    class Meta:
        model = Event
        widgets = {
            'start_date': DateInput(attrs={'type':'date'}),
            'end_date': DateInput(attrs={'type':'date'}),
            'start_hm': TimeInput(attrs={'type':'time'}, format='%H:%M'),
            'end_hm': TimeInput(attrs={'type':'time'}, format='%H:%M'),
        }
        exclude = ['start_time', 'end_time',]
        labels = {
            'start_hm':('Start time'),
            'end_hm':('End time'),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        form = super(EventForm, self).save(commit=False)
        start_time = datetime.combine(self.cleaned_data['start_date'], self.cleaned_data['start_hm'])
        end_time = datetime.combine(self.cleaned_data['end_date'], self.cleaned_data['end_hm'])
        form.start_time = start_time
        form.end_time = end_time
        print(start_time)
        if commit:
            form.save()
        return form