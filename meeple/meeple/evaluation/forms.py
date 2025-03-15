"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene los forms del proyecto evaluation
"""
from django import forms
from .models import User, Questionnaire, Section, Question, Choice, Algorithm
from django.forms import modelformset_factory, inlineformset_factory
from nested_formset import nestedformset_factory


class SignUpForm(forms.ModelForm):
    """Formulario para el registro

    Args:
        forms (ModelForm): hace referencia a una clase de formulario basada en un modelo en Django
    """
    password = forms.CharField(widget=forms.PasswordInput)  # Para manejar el input de contraseña

    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        model = User
        fields = ['username', 'password', 'email', 'location', 'age', 'rol', 'frequencyGame', 'expertiseGame']

    def save(self, commit=True):
        """Sobrescribe el método save de un ModelForm en Django para establecer la contraseña de un usuario de forma segura antes de guardarlo en la base de datos.

        Args:
            commit (bool, optional): Indica si se debe guardar el objeto inmediatamente en la base de datos. Por defecto es True.

        Returns:
            user: Devuelve el objeto guardado (en este caso, un usuario).
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Establecer la contraseña de forma segura
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
        fields = ['name', 'description', 'language', 'algorithm']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['name'].widget.attrs.update({'id': 'q-name'})

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
        fields = ['title']
    
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
