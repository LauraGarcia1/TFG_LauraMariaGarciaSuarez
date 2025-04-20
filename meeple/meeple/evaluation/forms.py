"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene los forms del proyecto evaluation
"""
from django import forms
from .models import Creator, Participant, User, Questionnaire, Section, Question, Choice, Algorithm
from django.forms import modelformset_factory, inlineformset_factory
from nested_formset import nestedformset_factory


class SignUpForm(forms.ModelForm):
    """Formulario para el registro de usuarios, permitiendo elegir entre Creator o Participant."""

    USER_TYPE_CHOICES = [
            ('CR', 'Creator'),
            ('PT', 'Participant')
        ]
    
    rol = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True, widget=forms.RadioSelect, label="rol")
    email = forms.EmailField(required=True)
    location = forms.CharField(max_length=200, required=False)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    # Campos específicos de Participant
    gender = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        required=False
    )
    frequencyGame = forms.ChoiceField(
        choices=[
            ('N', 'Never'),
            ('L', 'Once in a lifetime'),
            ('W', 'Once in a week'),
            ('MW', 'More than once in a week')
        ],
        required=False
    )
    expertiseGame = forms.ChoiceField(
        choices=[
            ('B', 'Beginner'),
            ('I', 'Intermediate'),
            ('A', 'Advanced')
        ],
        required=False
    )

    class Meta:
        """Configura el modelo y los campos del formulario"""
        model = User  # Base, pero cambiará en save()
        fields = ['username', 'password', 'email', 'location', 'birthdate', 'rol', 
                  'gender', 'frequencyGame', 'expertiseGame']

    def save(self, commit=True):
        """Crea un usuario como Creator o Participant según la selección."""
        rol = self.cleaned_data["rol"]

        if rol == "CR" or rol == "Creator":
            user = Creator(
                username=self.cleaned_data["username"],
                rol=self.cleaned_data["rol"],
                email=self.cleaned_data["email"],
                location=self.cleaned_data["location"],
                birthdate=self.cleaned_data["birthdate"]
            )
        else:  # Participant
            user = Participant(
                username=self.cleaned_data["username"],
                rol=self.cleaned_data["rol"],
                email=self.cleaned_data["email"],
                location=self.cleaned_data["location"],
                birthdate=self.cleaned_data["birthdate"],
                gender=self.cleaned_data["gender"],
                frequencyGame=self.cleaned_data["frequencyGame"],
                expertiseGame=self.cleaned_data["expertiseGame"]
            )

        user.set_password(self.cleaned_data["password"])  # Hash de la contraseña
        
        if commit:
            user.save()
        
        return user


class QuestionnaireForm(forms.ModelForm):
    """Formulario para el cuestionario

    Args:
        forms (ModelForm): hace referencia a una clase de formulario basada en un modelo en Django
    """
    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        model = Questionnaire
        fields = ['name', 'description', 'language']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['name'].widget.attrs.update({
                'id': 'q-name',
                'class': 'w-100',
                })

class SectionForm(forms.ModelForm):
    """Formulario para las secciones

    Args:
        forms (ModelForm): hace referencia a una clase de formulario basada en un modelo en Django

    Raises:
        forms.ValidationError: Si el campo title está vacío, se lanza una excepción de validación.

    Returns:
        Section: El objeto `Section` validado y guardado en la base de datos.
    """
    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        model = Section
        fields = ['title', 'algorithm']
    
    def clean_title(self):
        """Valida el campo 'title' para asegurarse de que no esté vacío.

        Raises:
            forms.ValidationError: Si el campo title está vacío, se lanza una excepción de validación.

        Returns:
            str: El valor limpio del campo 'title'.
        """
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Este campo es obligatorio.")
        return title
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['algorithm'].required = False  # Hace que el campo sea opcional
        self.fields['title'].widget.attrs.update({
            'class': 'w-100',
        })

class QuestionForm(forms.ModelForm):
    """Formulario para las preguntas

    Args:
        forms (ModelForm): hace referencia a una clase de formulario basada en un modelo en Django
    """
    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        model = Question
        fields = ['question_text', 'type']
        exclude = ['date_created', 'language']
    
    def __init__(self, *args, **kwargs):
        """Inicializa el formulario y personaliza los atributos de los widgets.
        """
        super().__init__(*args, **kwargs)
        self.fields['question_text'].widget.attrs.update({
            'data-index': '__qindex__',
            'data-section-index': '__section_index__',
            'class': 'w-100',
        })
        self.fields['type'].widget.attrs.update({
            'data-index': '__qindex__',
            'data-section-index': '__section_index__',
        })

class ChoiceForm(forms.ModelForm):
    """Formulario para las opciones

    Args:
        forms (ModelForm): hace referencia a una clase de formulario basada en un modelo en Django
    """
    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        model = Choice
        fields = ['choice_text']

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario y personaliza los atributos de los widgets.
        """
        super().__init__(*args, **kwargs)
        self.fields['choice_text'].widget.attrs.update({
            'data-index': '__cindex__',
            'data-section-index': '__sindexc__',
            'data-question-index': '__qindexc__',
            'class': 'w-100',
        })

class AlgorithmForm(forms.ModelForm):
    """Formulario para los algoritmos

    Args:
        forms (ModelForm): hace referencia a una clase de formulario basada en un modelo en Django
    """
    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        model = Algorithm
        fields = ["name", "description", "code", "type"]

# Para crear forms anidados fuera del administrador de Django
ChoiceFormSet = inlineformset_factory(Question, Choice, form=ChoiceForm, extra=1, can_delete=True)
QuestionFormSet = nestedformset_factory(Section, Question, form=QuestionForm, nested_formset=ChoiceFormSet, extra=1, can_delete=True)
SectionFormSet = modelformset_factory(Section, form=SectionForm, extra=1, can_delete=True)
