# Creator: Laura María García Suarez
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Questionnarie, Section, Question, Choice
from django.forms import modelformset_factory, inlineformset_factory
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
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Este campo es obligatorio.")
        return title

# Formulario para Question
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'type', 'language']
        exclude = ['date_created']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'data-index': '__qindex__',
            'data-section-index': '__section_index__',
        })
        self.fields['type'].widget.attrs.update({
            'data-index': '__qindex__',
            'data-section-index': '__section_index__',
        })
        self.fields['language'].widget.attrs.update({
            'data-index': '__qindex__',
            'data-section-index': '__section_index__',
        })

# Formulario para Question
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({
            'data-index': '__cindex__',
            'data-section-index': '__sindexc__',
            'data-question-index': '__qindexc__',
        })

# Librería para crear forms anidados
ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=1, can_delete=True)
QuestionFormSet = nestedformset_factory(Section, Question, form=QuestionForm, nested_formset=ChoiceFormSet, extra=1)
SectionFormSet = modelformset_factory(Section, form=SectionForm, extra=1)
