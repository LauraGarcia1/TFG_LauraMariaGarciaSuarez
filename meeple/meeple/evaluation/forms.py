# Creator: Laura María García Suarez
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Questionnarie, Section, Question, Choice
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from nested_formset import nestedformset_factory


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

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['name'].widget.attrs.update({'id': 'q-name'})

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
        exclude = ['date_created']

# Formulario para Question
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']

"""
# Formset para añadir Sections dentro de Questionnarie
SectionFormSet = inlineformset_factory(
    Questionnarie, Section, form=SectionForm, extra=1, can_delete=True
)

# Formset para añadir Questions dentro de Section
QuestionFormSet = inlineformset_factory(
    Section, Question, form=QuestionForm, extra=1, can_delete=True
)

# Formset para añadir Choice dentro de Question
ChoiceFormSet = inlineformset_factory(
    Question, Choice, form=ChoiceForm, extra=1, can_delete=True
)
"""

# Librería para crear forms anidados
ChoiceFormSet = nestedformset_factory(Question, Choice, form=ChoiceForm, nested_formset={}, extra=1)
QuestionFormSet = nestedformset_factory(Section, Question, form=QuestionForm, nested_formset=ChoiceFormSet, extra=1)
SectionFormSet = nestedformset_factory(Questionnarie, Section, form=SectionForm, nested_formset=QuestionFormSet, extra=1)
