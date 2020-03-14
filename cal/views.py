from datetime import datetime, timedelta
import calendar
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
        d = get_date(self.request.GET.get('month', None))
        cal = MonthlyCalendar(d.year, d.month)
        html_cal = cal.format()
        context['monthlycalendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def prev_month(d):
    first = d.replace(day=1)    # the first of the current month
    prev_month_end = first - timedelta(days=1)  # the day before the first of this month is in last month
    month = 'month=' + str(prev_month_end.year) + '-' + str(prev_month_end.month)   # use that to get the month before the current one
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1] # length of current month
    last = d.replace(day=days_in_month) # find last day of current month
    next_month = last + timedelta(days=1)   # day after last of this month is in next month
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def get_date(day):
    if day:
        year, month = (int(x) for x in day.split('-'))
        return datetime(year, month, day=1)
    return datetime.today()

def index(request):
    return HttpResponse('hi')