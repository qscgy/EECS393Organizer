from django.test import TestCase, RequestFactory, Client
from django.core.exceptions import ValidationError
from .models import Event, Metadata
from .forms import EventForm
from django.contrib.auth.forms import UserCreationForm
from datetime import date, time, datetime, timezone, timedelta
from django.shortcuts import reverse, get_object_or_404
from . import views, utils
from django.urls import resolve
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class DCViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.c = Client()
        logged_in = cls.c.login(username='testuser', password='12345')

    def test_is_list(self):
        '''
        Test if the DailyCalendarView is actually a list.
        '''
        form_data = {'title':'something', 'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data, user=self.user)
        sv = form.save()
        response = self.c.get(f'{reverse("cal:dailycalendar")}?date={utils.date2str(2020, 4, 17)}')
        print(response.content)
        self.assertTrue('<li>' in response.content.decode())

class UserCreationTests(TestCase):
    def test_create_user(self):
        form_data = {'username':'testuser', 'password1':'passwrod', 'password2':'passwrod'}
        form = UserCreationForm(data=form_data)
        form.save()
        
class CanvasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.c = Client()
        logged_in = cls.c.login(username='testuser', password='12345')

        md = Metadata(user=cls.user)
        md.last_canvas_call = datetime(2020, 1, 1)
        md.save()

        cls.canv_user, cls.courses, cls.assignments = views.access_canvas(cls.user)
    
    def test_canvas_call(self):
        '''
        Test that the Canvas API call does not return empty lists when it should not.
        '''
        md = get_object_or_404(Metadata, user=self.user)
        md.last_canvas_call += timedelta(days=-90)
        md.save()
        user, courses, assignments = views.access_canvas(self.user)
        print(md.last_canvas_call)
        self.assertTrue(len(user.__str__()) > 0)
        self.assertTrue(courses[0] is not None)
        self.assertTrue(len(assignments) > 0)
    
    def test_change_date(self):
        '''
        Test that the Canvas API will retrieve new assignments when they exist, and won't return when they don't.
        Combined into one method to reduce the number of external API calls, which take time and may raise
        security alerts.
        '''
        user, courses, assignments = views.access_canvas(self.user)
        md = get_object_or_404(Metadata, user=self.user)
        md.last_canvas_call += timedelta(days=-90)
        md.save()
        user, courses, assignments = views.access_canvas(self.user)
        self.assertTrue(len(assignments) > 0)
        user, courses, assignments = views.access_canvas(self.user)
        self.assertEquals(len(assignments), 0)
    
class EventModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.c = Client()
        logged_in = cls.c.login(username='testuser', password='12345')

    def test_needs_date(self):
        '''
        Tests if the start date is required.
        '''
        self.assertRaises(TypeError, lambda : Event.objects.create(user=self.user, title='something', start_time=time(11,20)))

    def test_blank_title(self):
        '''
        Test the behavior when a title is not provided.
        '''
        event = Event.objects.create(user=self.user, start_time=date(2020,4,17))
        self.assertEquals(event.title, '')
    
    def test_date_start_time(self):
        try:
            event = Event.objects.create(user=self.user, title='evt', start_time=date(202,4,16))
        except:
            self.fail('This event should be valid')

    def test_all_fields(self):
        '''
        Tests that no errors are raised when all fields are filled out.
        '''
        event = Event.objects.create(start_time=datetime(2020,4,17,hour=1,minute=1,second=1), title='t', description='yes',
         end_time=datetime(2020,4,17,hour=1,minute=2,second=1))
        
    def test_persistence(self):
        '''
        Tests that events can be saved and loaded.
        '''
        form_data = {'title':'something', 'start_time':date(2020, 4, 17)}
        event = Event.objects.create(**form_data)
        event.save()
        evt_id = event.id
        try:
            ev2 = Event.objects.get(pk=evt_id)
        except:
            self.fail('Loading a saved event should not raise an exception')

class EventFormTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.c = Client()
        logged_in = cls.c.login(username='testuser', password='12345')
    
    # Test if the start date field is required
    def test_needs_start_date(self):
        '''
        Tests that the form validation catches a lack of start date.
        '''
        form_data = {'title':'something'}
        form = EventForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
    
    # Test if the title field is required
    def test_needs_title(self):
        '''
        Tests that the form validation catches a lack of title.
        '''
        form_data = {'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
    
    # Test if anything but the start date and title are required
    def test_optionals(self):
        form_data = {'title':'something', 'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_persistence(self):
        '''
        Tests whether saved events are loaded without data changing.
        '''
        form_data = {'title':'something', 'start_date':date(2020, 4, 17)}
        form = EventForm(data=form_data, user=self.user)
        sv = form.save()
        evt = Event.objects.get(pk=sv.pk)
        self.assertEquals(evt.title, form_data['title'])
        self.assertEquals(evt.start_date, form_data['start_date'])
    
    def test_edit_view(self):
        '''
        Tests that the event_edit path loads.
        '''
        event = Event.objects.create(start_time=date(2020,4,17), user=self.user)
        evt_id = event.id
        req = self.rf.post(f'event/delete/{evt_id}')
        req.user = self.user
        try:
            response = views.event(req, event_id=evt_id)
        except:
            self.fail('Calling event should not raise an exception')
    
    def test_delete_perms(self):
        '''
        Tests that a user cannot delete an event that is not theirs.
        '''
        event = Event.objects.create(start_time=date(2020,4,17))
        evt_id = event.id
        req = self.rf.post(f'event/delete/{evt_id}')
        req.user = self.user
        self.assertRaises(PermissionDenied, lambda:views.delete_event(req, event_id=evt_id))

    def test_delete_view(self):
        '''
        Tests whether event_delete deletes events.
        '''
        event = Event.objects.create(user=self.user, start_time=date(2020,4,17))
        evt_id = event.id
        req = self.rf.post(f'event/delete/{evt_id}')
        req.user = self.user
        response = views.delete_event(req, event_id=evt_id)
        self.assertRaises(Event.DoesNotExist, lambda : Event.objects.get(pk=evt_id))

class PageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.user.set_password('12345')
        cls.user.save()
        cls.c = Client()
        logged_in = cls.c.login(username='testuser', password='12345')
    
    def test_home_is_monthlycalendar(self):
        '''
        Tests that the home page is a MonthlyCalendarView.
        '''
        found = resolve('/')
        self.assertEquals(type(found.func), type(views.MonthlyCalendarView.as_view()))
    
    def test_monthlycalendar_is_table(self):
        '''
        Tests that the monthlycalendar is a table with at least one cell.
        '''
        response = self.c.get(reverse('cal:monthlycalendar'))
        print(response.content)
        self.assertContains(response, '<td>', html=True, status_code=200)