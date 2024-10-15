from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class User(AbstractUser):
    ''' Default user class '''
    name = models.CharField(max_length=150)  # Campo para el nombre del usuario
    email = models.EmailField(unique=True)  # Campo de correo electrónico, debe ser único
    location = models.CharField(max_length=255, blank=True, null=True)  # Ubicación opcional
    age = models.PositiveIntegerField(blank=True, null=True)  # Edad opcional
    frequencyGame = models.CharField(max_length=100, blank=True, null=True)  # Frecuencia de juego
    expertiseGame = models.CharField(max_length=100, blank=True, null=True)  # Especialidad en juegos

    USERNAME_FIELD = 'username'  # Campo que se utiliza para autenticar
    REQUIRED_FIELDS = ['name', 'email']  # Campos requeridos al crear un usuario

    def __str__(self):
        return self.username
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)  # Valida la contraseña usando los validadores definidos en settings.py
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Validar el formato del email
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Please enter a valid email address.')

        # Validar dominio (opcional)
        allowed_domains = ["gmail.com", "yahoo.com"]
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(f"Only email addresses from {', '.join(allowed_domains)} are allowed.")

        return email