from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class User(AbstractUser):
    ''' Default user class with extra fields '''
    name = models.CharField(max_length=150)  # Field for user name
    email = models.EmailField(unique=True)  # Field for unique email
    #location = models.CharField(max_length=255, blank=True, null=True)  # Field for location, optional
    location = models.CharField(max_length=255)  # Field for location
    age = models.PositiveIntegerField()  # Field for age
    frequencyGame = models.CharField(max_length=100, blank=True, null=True)  # Field for game frequency
    expertiseGame = models.CharField(max_length=100, blank=True, null=True)  # Field for gaming expertise

    USERNAME_FIELD = 'username'  # Field used to authenticate
    REQUIRED_FIELDS = ['name', 'email', 'location', ]  # Required fields to create the user

    def __str__(self):
        return self.username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Validate password using the validation defined in settings.py
        validate_password(password)
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Please enter a valid email address.')

        # Validate domain
        allowed_domains = ["gmail.com", "yahoo.com"]
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(f"Only email addresses from {', '.join(allowed_domains)} are allowed.")

        return email
    
class Preferences(models.Model):
    preference = models.CharField(max_length=50)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.name)