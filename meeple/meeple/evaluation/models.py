"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene los modelos del proyecto evaluation
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings


class User(AbstractUser):
    """Clase Usuario predeterminada con extra parámetros

    Args:
        AbstractUser (AbstractUser): Proporciona los campos y métodos base para el modelo de usuario predeterminado de Django.

    Raises:
        ValidationError: Si el correo electrónico no es válido o no pertenece a un dominio permitido.
        ValidationError: Si la contraseña no cumple con los requisitos de validación.

    Returns:
        User: Un objeto de usuario personalizado con los campos adicionales y validaciones.
    """
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    birthdate = models.DateField(null=True)
    rol = models.CharField(
        max_length = 5,
        choices = [
            ('CR', 'Creator'),
            ('PT', 'Participant')
        ],
        default='PT'
    )
    frequencyGame = models.CharField(
        max_length = 10,
        choices = [
            ('N', 'Never'),
            ('L', 'Once in a lifetime'),
            ('W', 'Once in a week'),
            ('MW', 'More than once in a week')
        ],
        default='N'
    )
    expertiseGame = models.CharField(
        max_length = 10,
        choices = [
            ('B', 'Beginner'),
            ('I', 'Intermediate'),
            ('A', 'Advanced')
        ],
        default='B'
    )
    gender = models.CharField(
        max_length = 10,
        choices = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ],
        default='O'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'email', 'location', 'birthdate', 'frequencyGame', 'expertiseGame']

    def __str__(self):
        """Devuelve el nombre de usuario como representación del objeto.

        Returns:
            str: Nombre de usuario del usuario.
        """
        return self.username
    
    def clean_password(self):
        """Valida la contraseña del usuario.

        Returns:
            str: La contraseña limpia y validada.
        """
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password
    
    def clean_email(self):
        """Valida el correo electrónico del usuario.

        Raises:
            ValidationError: Si el correo electrónico no es válido o no pertenece a un dominio permitido.

        Returns:
            str: El correo electrónico limpio y validado.
        """
        email = self.cleaned_data.get('email')

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('Please enter a valid email address.')

        allowed_domains = ["gmail.com", "yahoo.com"]
        domain = email.split('@')[-1]
        if domain not in allowed_domains:
            raise ValidationError(f"Only email addresses from {', '.join(allowed_domains)} are allowed.")

        return email
    
    def __str__(self):
        """Devuelve una representación en cadena del objeto Usuario.

        Returns:
            str: Una cadena con el nombre de usuario del usuario.
        """
        return f"Username: {self.username}"

class Algorithm(models.Model):
    """Modelo que representa un algoritmo de recomendación.

    Args:
        models (Model): Base para definir campos y relaciones en un modelo de Django.

    Returns:
        Algorithm: Un objeto que representa un algoritmo de recomendación.
    """
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=15)
    description = models.TextField()
    code = models.TextField(help_text="You must define a function with header 'recommend(user, responses)' that returns a list of games.", null=True)
    type = models.CharField(
        max_length = 20,
        choices = [
            ('collaborative', 'Collaborative Filtering'),
            ('content', 'Content-based Filtering'),
            ('hybrid', 'Hybrid'),
            ('rules', 'Rule-Based'),
            ('contextual', 'Contextual'),
            ('random', 'Random'),
            ('deep_learning', 'Deep learning')
        ],
        default='hybrid'
    )

    def __str__(self):
        """Devuelve una representación en cadena de la respuesta.

        Returns:
            str: Una cadena con la información clave de la respuesta.
        """
        return f"Algorithm name: {self.name}"

class Questionnaire(models.Model):
    """Modelo que representa un cuestionario.

    Args:
        models (Model): Base para definir campos y relaciones en un modelo de Django.

    Returns:
        Questionnaire: Un objeto que representa un cuestionario.
    """
    name = models.CharField(max_length=150, blank=False, null=False)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    uploaded = models.BooleanField(default=False)
    algorithm = models.ForeignKey(Algorithm, related_name='algorithm', on_delete=models.SET_NULL, null=True)
    language = models.CharField(
        max_length = 10,
        choices = [
            ('EN', 'English'),
            ('ES', 'Español')
        ],
        default='EN'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def are_fields_filled(self):
        """Método para comprobar si los campos están rellenos

        Returns:
            bool: Devuelve True si description, name, algorithm y language tiene contenido, False si está vacío.
        """
        return bool(self.description and self.name and self.algorithm and self.language)

    def __str__(self):
        """Devuelve una representación en cadena de la respuesta.

        Returns:
            str: Una cadena con la información clave de la respuesta.
        """
        return f"Questionnaire name: {self.name}\nQuestionnaire id: {self.id}"

class Section(models.Model):
    """Modelo que representa una sección dentro de un cuestionario.

    Args:
        models (Model): Base para definir campos y relaciones en un modelo de Django.

    Returns:
        Section: Un objeto que representa una sección dentro de un cuestionario.
    """
    questionnaire = models.ForeignKey(Questionnaire, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)

    def are_fields_filled(self):
        """Método para comprobar si los campos están rellenos

        Returns:
            bool: Devuelve True si title tiene contenido, False si está vacío.
        """
        return bool(self.title)

    def __str__(self):
        """Devuelve una representación en cadena de la respuesta.

        Returns:
            str: Una cadena con la información clave de la respuesta.
        """
        return f"Section title: {self.title}\nSection id: {self.id}"

class Question(models.Model):
    """Modelo que representa una pregunta dentro de una sección.

    Args:
        models (Model): Base para definir campos y relaciones en un modelo de Django.

    Returns:
        Question: Un objeto que representa una pregunta dentro de una sección.
    """
    section = models.ForeignKey('Section', on_delete=models.CASCADE, null=False, related_name='questions')
    date_created = models.DateTimeField(auto_now_add=True)
    question_text = models.CharField(max_length=150, blank=False, null=False)
    # TODO: tendría sentido que hubiese otros tipos?
    type = models.CharField(
        max_length=20,
        choices=[
            ('SCRB', 'Single choice radio buttons'),
            ('MCRB', 'Multiple choice radio buttons'),
            ('SCCB', 'Single choice combo box'),
            ('MCCB', 'Multiple choice combo box'),
            ('OAS', 'Open answer short'),
            ('OAL', 'Open answer long'),
            ('N', 'Number')
        ],
        default='OAS'
        )
    language = models.CharField(
        max_length = 10,
        choices = [
            ('EN', 'English'),
            ('ES', 'Español')
        ],
        default='EN'
    )

    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        ordering = ['date_created']

    def are_fields_filled(self):
        """Método para comprobar si los campos están rellenos

        Returns:
            bool: Devuelve True si question_text, type y language tiene contenido, False si está vacío.
        """
        return bool(self.type and self.language and self.question_text)
    
    def __str__(self):
        """Devuelve una representación en cadena de la respuesta.

        Returns:
            str: Una cadena con la información clave de la respuesta.
        """
        return f"Question text: {self.question_text}\nQuestion id: {self.id}"
    
class Choice(models.Model):
    """Modelo que representa una opción de respuesta a una pregunta.

    Args:
        models (Model): Base para definir campos y relaciones en un modelo de Django.

    Returns:
        Choice: Un objeto que representa una opción de respuesta para una pregunta.
    """
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, related_name='choices')
    choice_text = models.CharField(max_length=50, blank=True, null=True)

    def are_fields_filled(self):
        """Método para comprobar si los campos están rellenos

        Returns:
            bool: Devuelve True si choice_text tiene contenido, False si está vacío.
        """
        return bool(self.choice_text)

    def __str__(self):
        """Devuelve una representación en cadena de la respuesta.

        Returns:
            str: Una cadena con la información clave de la respuesta.
        """
        return f"Choice text: {self.choice_text}"
    

class Answer(models.Model):
    """Modelo que representa una respuesta a una pregunta, proporcionada por un usuario.

    Args:
        models (Model): Base para definir campos y relaciones en un modelo de Django.

    Returns:
        Answer: Un objeto que representa una respuesta a una pregunta.
    """
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=False)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=250, blank=True, null=True)
    choice = models.ForeignKey('Choice', on_delete=models.SET_NULL, null=True)
    language = models.CharField(
        max_length = 10,
        choices = [
            ('en', 'English'),
            ('es', 'Español')
        ],
        default='en'
    )

    class Meta:
        """Configura el modelo, los campos y opciones del formulario en un ModelForm de Django.
        """
        ordering = ['date_created']

    def __str__(self):
        """Devuelve una representación en cadena de la respuesta.

        Returns:
            str: Una cadena con la información clave de la respuesta.
        """
        return f"Answer choice: {self.choice}\nAnswer text: {self.text}\nAnswer id: {self.id}"

class Recommendation(models.Model):
    """Modelo que representa una recomendación generada por un algoritmo, asociada a un juego y sus métricas.

    Args:
        models (Model): Proporciona la base para definir campos y relaciones en un modelo de Django.

    Returns:
        Recommendation: Un objeto que representa una recomendación para un juego generado por un algoritmo.
    """
    algorithm = models.ForeignKey('Algorithm', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.SET_NULL, null=True)
    metrics = models.JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True)

    def add_metrics(self, new_metrics):
        """Añade nuevas métricas a la recomendación.

        Args:
            new_metrics (dict): Nuevas métricas a agregar a la recomendación.
        """
        self.metrics.extend(new_metrics)
        self.save()

    def __str__(self):
        """Devuelve una representación en cadena de la recomendación.

        Returns:
            str: Una cadena con la información clave de la recomendación.
        """
        return f"Recommendation algorithm: {self.algorithm}\nRecommendation game: {self.game}\nRecommendation metrics: {self.metrics}\nRecommendation id: {self.id}"

class Game(models.Model):
    """Modelo que representa un juego, identificado por un ID de la Base de Datos del TFG de Andrea Salcedo López.

    Args:
        models (Model): Proporciona la base para definir campos y relaciones en un modelo de Django.

    Returns:
        Game: Un objeto que representa un juego con un ID de la Base de Datos del TFG de Andrea Salcedo López.
    """
    id_BGG = models.IntegerField(default=0)

    def __str__(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return f"Game id: {self.id}\nBGG id: {self.id_BGG}"

class Evaluation(models.Model):
    """Modelo que almacena las evaluaciones realizadas por un usuario sobre una recomendación.

    Args:
        models: Proporciona la base para definir campos y relaciones en un modelo de Django.

    Returns:
        Evaluation: Un objeto que representa una evaluación de recomendación por parte de un usuario.
    """
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    answers = models.JSONField(default=list)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Devuelve una representación en cadena de la evaluación.

        Returns:
            str: Una cadena con el usuario, la recomendación y el ID de la evaluación.
        """
        return f"Evaluation user: {self.user}\nEvaluation recommendation: {self.recommendation}\nEvaluation id: {self.id}"

class Preference(models.Model):
    """Modelo que almacena las preferencias de un usuario en relación a un juego.

    Args:
        models (Model): Proporciona la base para definir campos y relaciones en un modelo de Django.

    Returns:
        Preference: Un objeto que representa las preferencias del usuario relacionadas con un juego.
    """
    text = models.ForeignKey('Game', on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    context = models.CharField(max_length=100, blank=True, null=True)
    value = models.FloatField(default=0.0) # TODO: Es necesario?
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        """Devuelve una representación en cadena de la preferencia.

        Returns:
            str: Una cadena con el usuario, la categoría, el contexto y el ID de la preferencia.
        """
        return f"Preference user: {self.user}\nPreference categories: {self.category}\nPreference categories: {self.context}\nPreference id: {self.id}"

