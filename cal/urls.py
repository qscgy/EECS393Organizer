from django.conf.urls import url
from . import views

app_name = 'cal'
urlpatterns = [
    url(r'^$', views.LoginView.as_view(), name='login'),
    url(r'^monthlycalendar/$', views.MonthlyCalendarView.as_view(), name='monthlycalendar'),
    url(r'^event/new/$', views.event, name='event_new'),
    url(r'^event/edit/(?P<event_id>\d+)/$', views.event, name='event_edit'),
    url(r'^dailycalendar/$', views.DailyCalendarView.as_view(), name='dailycalendar'),
]