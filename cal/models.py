from django.db import models

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)

    class Meta:
        ordering = ['-start_time', '-title']

    def __str__(self):
        '''
        String representation of an Event object.
        '''
        return self.title
    
    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])
