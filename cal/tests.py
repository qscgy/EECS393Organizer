from django.test import TestCase, RequestFactory, Client
from django.core.exceptions import ValidationError
from .models import Event, Metadata
from .forms import EventForm
from datetime import date, time, datetime, timezone, timedelta
from django.shortcuts import reverse
from . import views, utils
from django.urls import resolve

class DCViewTests(TestCase):
    def test_is_list(self):
        form_data = {'title':'something', 'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data)
        sv = form.save()
        c = Client()
        response = c.get(f'{reverse("cal:dailycalendar")}?date={utils.date2str(2020, 4, 17)}')
        print(response.content)
        self.assertTrue('<li>' in response.content.decode())

class CanvasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user, cls.courses, cls.assignments = views.access_canvas()
    
    def test_canvas_call(self):
        md = Metadata.load()
        md.last_canvas_call += timedelta(days=-90)
        md.save()
        user, courses, assignments = views.access_canvas()
        print(md.last_canvas_call)
        self.assertTrue(len(user.__str__()) > 0)
        self.assertTrue(courses[0] is not None)
        self.assertTrue(len(assignments) > 0)
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

    def test_blank_title(self):
        event = Event.objects.create(start_time=date(2020,4,17))
        self.assertEquals(event.title, '')

    def test_all_fields(self):
        event = Event.objects.create(start_time=datetime(2020,4,17,hour=1,minute=1,second=1), title='t', description='yes',
         end_time=datetime(2020,4,17,hour=1,minute=1,second=1))
        
    def test_persistence(self):
        form_data = {'title':'something', 'start_time':date(2020, 4, 17)}
        event = Event.objects.create(**form_data)
        event.save()
        ev2 = Event.objects.get(pk=event.id)

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
    
    def test_persistence(self):
        form_data = {'title':'something', 'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data)
        sv = form.save()
        evt = Event.objects.get(pk=sv.pk)
        self.assertEquals(evt.title, form_data['title'])
        self.assertEquals(evt.start_date, form_data['start_date'])

class PageTests(TestCase):
    def test_home_is_monthlycalendar(self):
        found = resolve('/')
        self.assertEquals(type(found.func), type(views.MonthlyCalendarView.as_view()))
    
    def test_home_is_table(self):
        c = Client()
        response = c.get(reverse('cal:monthlycalendar'))
        self.assertContains(response, '<td>', html=True, status_code=200)