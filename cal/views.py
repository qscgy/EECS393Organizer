from datetime import datetime, timedelta, date
import calendar
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from .models import *
from .utils import MonthlyCalendar
from .forms import EventForm

class LoginView(generic.TemplateView):
    template_name = 'cal/login.html'

class GetCanvasView(generci.TemplateView):
    template_name = 'cal/load_canvas.html'

class DailyCalendarView(generic.ListView):
    model = Event
    context_object_name = 'event_list'
    template_name = 'cal/dailycalendar.html'

    def get_queryset(self):
        self.datestring = self.request.GET.get('date', None)
        self.day = date.fromisoformat(self.datestring)
        return Event.objects.filter(start_time__contains=self.day)

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

def event(request, event_id=None):
    instance = Event()
    if event_id:    # If the event id is given, get the corresponding object so it can be edited
        instance = get_object_or_404(Event, pk=event_id)
    else:   # otherwise, use a blank Event
        instance = Event()
    
    form = EventForm(request.POST or None, instance=instance)   # create a form to create or edit the event
    if request.POST and form.is_valid():
        # save the edited Event
        form.save()
        return HttpResponseRedirect(reverse('cal:monthlycalendar'))
    return render(request, 'cal/event.html', {'form':form, "evt_id":event_id})

def delete_event(request, event_id=None):
    instance = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        instance.delete()
        return HttpResponseRedirect(reverse('cal:monthlycalendar'))
    return render(request, 'cal/confirm_delete.html', {'evt_id':event_id})