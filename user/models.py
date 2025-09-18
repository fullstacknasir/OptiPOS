from django.contrib.auth.models import AbstractUser
from django.db import models

from core.models import Store


# Create your models here.
class User(AbstractUser):
    role = models.CharField(max_length=100,
                            choices=(('Admin', 'Admin'), ('Employee', 'Employee'), ('Cutomer', 'Cutomer')),
                            default='Customer')
    def __str__(self):
        return self.username
