from django.urls import path
from . import views

app_name = 'cal'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('monthlycalendar/', views.MonthlyCalendarView.as_view(), name='monthlycalendar'),
    path('event/new/', views.event, name='event_new'),
    path('event/edit/<int:event_id>/', views.event, name='event_edit'),
    path('dailycalendar/', views.DailyCalendarView.as_view(), name='dailycalendar'),
    path('event/delete/<int:event_id>', views.delete_event, name='event_delete'),
]