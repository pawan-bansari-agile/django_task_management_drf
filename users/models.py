from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def soft_delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.is_active = False
        self.save()

    def restore(self):
        self.is_deleted = False
        self.is_active = True
        self.save()