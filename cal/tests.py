from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Event
from .forms import EventForm
from datetime import date, time

class EventModelTests(TestCase):
    # Test if an event can be created with only a date and not a time provided for start_time
    e = ''
    def test_needs_date(self):
        self.assertRaises(TypeError, lambda : Event.objects.create(title='something', start_time=time(11,20)))

    def test_needs_title(self):
        event = Event.objects.create(start_time=date(2020,4,17))
        self.assertEquals(event.title, '')

class EventFormTests(TestCase):
    # Test if the start date field is required
    def test_needs_start_date(self):
        form_data = {'title':'something'}
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    # Test if the title field is required
    def test_needs_title(self):
        form_data = {'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    # Test if anything but the start date and title are required
    def test_optionals(self):
        form_data = {'title':'something', 'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())