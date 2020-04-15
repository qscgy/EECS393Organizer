from django.test import TestCase, RequestFactory
from django.core.exceptions import ValidationError
from .models import Event, Metadata
from .forms import EventForm
from datetime import date, time, datetime, timezone, timedelta
from django.shortcuts import reverse
from . import views

class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user, cls.courses, cls.assignments = views.access_canvas()
    
    def test_canvas_call(self):
        self.assertTrue(len(self.user.__str__()) > 0)
        self.assertTrue(self.courses[0] is not None)
        self.assertTrue(len(self.assignments) > 0)
        # for c in self.courses:
        #     try:
        #         print(c.name, c.__dict__['id'])
        #     except:
        #         print(c.__dict__)
        # for a in self.assignments:
        #     print(a)
    
    def test_metadata_updates(self):
        md = Metadata.load()
        self.assertTrue(md.last_canvas_call < datetime.now(timezone.utc))

class TimingTests(TestCase):
    def test_change_date(self):
        user, courses, assignments = views.access_canvas()
        md = Metadata.load()
        md.last_canvas_call += timedelta(days=-90)
        md.save()
        user, courses, assignments = views.access_canvas()
        self.assertTrue(len(assignments) > 0)


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