from django.conf.urls import url
from . import views

app_name = 'cal'
urlpatterns = [
    url(r'^$', views.LoginView.as_view(), name='login'),
    url(r'^monthlycalendar/$', views.MonthlyCalendarView.as_view(), name='monthlycalendar'),
]