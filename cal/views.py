from datetime import datetime, timedelta, date, timezone
import calendar
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import *
from .utils import MonthlyCalendar
from .forms import EventForm
from canvasapi import Canvas
from .local_settings import *
import pytz
import tzlocal

class LoginView(generic.TemplateView):
    template_name = 'cal/login.html'

class CanvasItemListView(generic.ListView):
    model = Event
    context_object_name = 'event_list'
    template_name = 'cal/canvas_item_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        user, courses, assignments = access_canvas(self.request.user)
        asgn_events = []
        for a in assignments:
            asgn_events.append(dict_to_event(a, user=self.request.user))
            asgn_events[-1].save()
        context['event_list'] = asgn_events
        return context

class DailyCalendarView(generic.ListView):
    model = Event
    context_object_name = 'event_list'
    template_name = 'cal/dailycalendar.html'

    def get_queryset(self):
        self.datestring = self.request.GET.get('date', None)
        self.day = date.fromisoformat(self.datestring)
        qs = Event.objects.filter(user=self.request.user, start_date__contains=self.day)
        return qs

class MonthlyCalendarView(generic.ListView):
    model = Event
    template_name = 'cal/monthlycalendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return None
        d = get_date(self.request.GET.get('month', None))
        cal = MonthlyCalendar(self.request, d.year, d.month)
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
    create_new = False
    if event_id:    # If the event id is given, get the corresponding object so it can be edited
        instance = get_object_or_404(Event, pk=event_id)
    else:   # otherwise, use a blank Event
        instance = Event()
        create_new=True
    
    if instance.user != request.user and not create_new:
        raise PermissionDenied

    form = EventForm(request.POST or None, instance=instance, user=request.user)   # create a form to create or edit the event
    if request.POST and form.is_valid():
        # save the edited Event
        form.save()
        return HttpResponseRedirect(reverse('cal:monthlycalendar'))
    return render(request, 'cal/event.html', {'form':form, "evt_id":event_id})

def delete_event(request, event_id=None):
    instance = get_object_or_404(Event, pk=event_id)

    if request.user != instance.user:
        raise PermissionDenied
    if request.method == 'POST':
        instance.delete()
        return HttpResponseRedirect(reverse('cal:monthlycalendar'))
    return render(request, 'cal/confirm_delete.html', {'evt_id':event_id})

def access_canvas(user):
    try:
        metadata = get_object_or_404(Metadata, user=user)
    except:
        metadata = Metadata()
        metadata.last_canvas_call = datetime(2020, 1, 1)
        metadata.user = user

    # Load the last call and localize it to UTC.
    last_call = metadata.last_canvas_call or pytz.utc.localize(datetime.utcnow())
    last_call = last_call.replace(tzinfo=pytz.UTC)

    # Set call_time to the time right before we make the API call.
    call_time = pytz.utc.localize(datetime.utcnow())

    canvas = Canvas(API_URL, API_KEY)
    user = canvas.get_current_user()
    courses = user.get_courses(enrollment_status='active')
    assignments = []

    # For each of the user's courses for the current term, finds all assignments created after last_call,
    # converts them to dictionaries, and adds them to a list.
    for c in courses:
        if 'enrollment_term_id' in c.__dict__.keys() and c.__dict__['enrollment_term_id']==108:
            asgn = c.get_assignments()
            for a in asgn:
                a = a.__dict__
                try:
                    created = pytz.utc.localize(datetime.strptime(a['created_at'], '%Y-%m-%dT%H:%M:%SZ'))
                    if datetime.strptime(a['due_at'], '%Y-%m-%dT%H:%M:%SZ') and created and created >= last_call:
                        a['course_name'] = c.name
                        assignments.append(a)
                except Exception as ex:
                    print('failing')
    
    metadata.last_canvas_call = call_time
    metadata.save()
    return user, courses, assignments

def dict_to_event(assignment, user):
    '''
    Takes an assignment (as a dictionary) and returns an event with the same name, start_time equal to the due date,
    and the course name as the description.
    '''
    dc = assignment
    st = pytz.utc.localize(datetime.strptime(dc['due_at'], '%Y-%m-%dT%H:%M:%SZ'))
    print(st)
    st2 = st.astimezone(tzlocal.get_localzone())
    ev = Event.objects.create(title=dc['name'], start_time=st2, start_date=st2.date(), start_hm=st2.time(),
     description=dc['course_name'], user=user)
    return ev

def error_500(request, *args, **kwargs):
    data = {}
    return render(request, 'cal/500.html', data)

def signup(request):
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('cal:monthlycalendar'))
    else:
        form = UserCreationForm()
    return render(request, 'cal/signup.html', {'form':form})
