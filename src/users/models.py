from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """
    Custom User model
    Extend default database table with extra columns: full_name and is_email_verified
    """
    full_name = models.CharField(max_length=200, blank=True)
    is_email_verified = models.BooleanField(default=False)