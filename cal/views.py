from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe
from .models import *
from .utils import MonthlyCalendar

class LoginView(generic.TemplateView):
    template_name = 'cal/login.html'

class MonthlyCalendarView(generic.ListView):
    model = Event
    template_name = 'cal/monthlycalendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = get_date(self.request.GET.get('day', None))
        cal = MonthlyCalendar(today.year, today.month)
        html_cal = cal.format()
        context['monthlycalendar'] = mark_safe(html_cal)
        return context

def get_date(day):
    if day:
        year, month = (int(x) for x in day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def index(request):
    return HttpResponse('hi')