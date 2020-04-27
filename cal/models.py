from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from datetime import date
from django.contrib.auth import get_user_model

# Create your models here.

class Metadata(models.Model):
    '''
    Class to store metadata for the user.
    '''
    last_canvas_call = models.DateTimeField(null=True)  # the last time the Canvas API was called
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super(Metadata, self).save(*args, **kwargs)
    
    def delete(self):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Event(models.Model):
    '''
    Class to represent a single calendar event. It can have a name, description, and start and end dates/times.
    '''
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
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
        '''
        Return the URL for this Event.
        '''
        url = reverse('cal:event_edit', args=(self.id,))
        return mark_safe(f'<a href=\"{url}\">{self.title}</a>')

    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])
