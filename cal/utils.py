from datetime import datetime, timedelta, date
from calendar import HTMLCalendar, SUNDAY
from .models import Event
from django.shortcuts import reverse
from django.utils.safestring import mark_safe
from canvasapi import Canvas
from django.conf import settings

class MonthlyCalendar(HTMLCalendar):
    def __init__(self, request, year=None, month=None):
        self.year = year
        self.user = request.user
        self.month = month
        super(MonthlyCalendar, self).__init__()
    
    def formatday(self, day, events):
        events_per_day = events.filter(user=self.user, start_date__day=day)
        d = ''
        for ev in events_per_day:
            d += f'<li>{ev.get_html_url}</li>'
        
        if day != 0:
            date = date2str(self.year, self.month, day)
            url = f'{reverse("cal:dailycalendar")}?date={date}'
            return f'<td class="day-cell" onclick="location.href=\'{url}\';"><span class=\"date\">{day}</span><ul>{d}</ul></td>'
        return '<td></td>'
    
    def formatweek(self, _week, events):
        week = ''
        for d, day in _week:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'
    
    def format(self, withyear=True):
        events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)
        
        self.setfirstweekday(SUNDAY)
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'

        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        
        return cal

def date2str(year, month, day):
    return date(year, month, day).isoformat()