# Creator: Laura María García Suarez
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Questionnarie, Section, Question
from django.forms import inlineformset_factory


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
        fields = ['name', 'description', 'language']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

# Formulario para Section
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title']

# Formulario para Question
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'type', 'language']

# Formset para añadir Sections dentro de Questionnarie
SectionFormSet = inlineformset_factory(
    Questionnarie, Section, form=SectionForm, extra=1, can_delete=True
)

# Formset para añadir Questions dentro de Section
QuestionFormSet = inlineformset_factory(
    Section, Question, form=QuestionForm, extra=1, can_delete=True
)
