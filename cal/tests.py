from django.test import TestCase
from .models import Event
from .forms import EventForm
from datetime import date

class EventTestCase(TestCase):
    def test_eventform_valid(self):
        instance = Event.objects.create(title='some event', start_date=date(2020, 4, 1))
        form = EventForm(instance=instance)
        self.assertEqual(form.is_valid(), True)
