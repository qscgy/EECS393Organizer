from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from datetime import date

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(default=date.today)
    start_hm = models.TimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_hm = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-start_time', '-title']

    def __str__(self):
        '''
        String representation of an Event object.
        '''
        return self.title
    
    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return mark_safe(f'<a href=\"{url}\">{self.title}</a>')

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])
