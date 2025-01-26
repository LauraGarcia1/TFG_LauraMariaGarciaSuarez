# Creator: Laura María García Suarez
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Questionnarie


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Para manejar el input de contraseña

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'location', 'age', 'rol', 'frequencyGame', 'expertiseGame']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Establecer la contraseña de forma segura
        if commit:
            user.save()
        return user

class QuestionnarieForm(forms.ModelForm):
    class Meta:
        model = Questionnarie
        fields = ['name', 'description', 'language']  # Campos que deseas permitir editar