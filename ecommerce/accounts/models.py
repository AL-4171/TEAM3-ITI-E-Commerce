# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
 
 
class User(AbstractUser):
    """
    Custom user model.
    - Login is done by EMAIL (unique), not username.
    - Phone must be a valid Egyptian mobile number.
    - first_name / last_name already exist on AbstractUser.
    """
 
    egyptian_phone_validator = RegexValidator(
        regex=r'^01[0125][0-9]{8}$',
        message="Enter a valid Egyptian phone number (e.g. 01012345678)."
    )
 
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=11,
        validators=[egyptian_phone_validator],
        unique=True,
    )
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'phone']
 
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
 
 