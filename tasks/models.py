from django.db import models
from django.conf import settings
from users.models import CustomUser

class Task(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    # assigned_to = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     blank=True,
    #     limit_choices_to={'role': 'staff'}
    # )
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'user'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    # attachments = models.FileField(upload_to='attachments/', null=True, blank=True)
    attachments = models.ManyToManyField('Attachment', blank=True)

    def archive(self):
        if self.status == 'completed':
            self.status = 'archived'
            self.save()
        else:
            raise ValueError("Only completed tasks can be archived.")
        
class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)