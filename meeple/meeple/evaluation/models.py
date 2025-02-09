from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings


class User(AbstractUser):
    ''' Default user class with extra fields '''
    email = models.EmailField(unique=True)  # Field for unique email
    location = models.CharField(max_length=200, blank=True, null=True)  # Field for location
    age = models.PositiveIntegerField()  # Field for age
    rol = models.CharField(
        max_length = 5,
        choices = [
            ('ER', 'Evaluator'),
            ('ED', 'Evaluated')
        ],
        default='ER'
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
    gender = models.CharField( # NEW
        max_length = 10,
        choices = [
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ],
        default='O'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'  # Field used to authenticate
    REQUIRED_FIELDS = ['password', 'email', 'location', 'age', 'frequencyGame', 'expertiseGame']  # Required fields to create the user

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
    
    def __str__(self):
        return self.username

class Interaction(models.Model):
    INTEREST_CHOICES = [
        (1, 'Not interested'),
        (2, 'Slightly interested'),
        (3, 'Neutral'),
        (4, 'Interested'),
        (5, 'Very interested'),
    ]
    GENERAL_CHOICES = [
        (1, 'Very unlikely'),
        (2, 'Unlikely'),
        (3, 'Neutral'),
        (4, 'Likely'),
        (5, 'Very likely'),
    ]
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, null=False, related_name='answers')
    gamerecommended = models.ForeignKey('GameRecommended', on_delete=models.CASCADE, null=False)
    interested = models.IntegerField(choices=INTEREST_CHOICES, default=3)
    buyorrecommend = models.IntegerField(choices=GENERAL_CHOICES, default=3)
    preference = models.BooleanField(default=False)
    # TODO: TextField??
    moreoptions = models.TextField()
    influences = models.JSONField(default=list)

    def __str__(self):
        return f"Evaluation for {self.gamerecommended}"
    
    def add_influences(self, add_influences):
        INFLUENCE_CHOICES = {
            '1': 'Price',
            '2': 'Quality',
            '3': 'Features',
            '4': 'Popularity',
            '5': 'Recommendations from other users',
            '6': 'Other'
        }
        [INFLUENCE_CHOICES[str(num)] for num in add_influences]
        self.influences.extend(add_influences)
        self.save()

class Questionnarie(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    language = models.CharField(
        max_length = 10,
        choices = [
            ('EN', 'English'),
            ('ES', 'Español')
        ],
        default='EN'
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Section(models.Model):
    questionnarie = models.ForeignKey(Questionnarie, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    section = models.ForeignKey('Section', on_delete=models.CASCADE, null=False, related_name='questions')
    date_created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=150, blank=False, null=False)
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
            ('R', 'Range'),
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
        ordering = ['date_created']
    
    def __str__(self):
        return f"{self.id} - {self.text}"
    
    

class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, related_name='choices')
    text = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.text}"
    

class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=False)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
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
        ordering = ['date_created']

    def __str__(self):
        return f"{self.id} - {self.choice}"

class Recommendation(models.Model):
    algorithm = models.ForeignKey('Algorithm', on_delete=models.CASCADE, null=False)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    # TODO: Cambiar parámetros en el diagrama
    metrics = models.JSONField(default=list)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.algorithm}"
    
    def add_metrics(self, new_metrics):
        self.metrics.extend(new_metrics)
        self.save()

class GameRecommended(models.Model):
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE, null=False, related_name="games")
    game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.recommendation} {self.game}"

class Game(models.Model): # ??
    id_BGG = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id_BGG)

class Algorithm(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=15)
    description = models.TextField()
    type = models.CharField(
        max_length = 20,
        choices = [
            ('collaborative', 'Collaborative Filtering'),
            ('content', 'Content-based Filtering'),
            ('hybrid', 'Hybrid'),
            ('rules', 'Rule-Based'),
            ('contextual', 'Contextual'),
            ('deep_learning', 'Deep learning')
        ],
        default='hybrid'
    ) # TODO: No sé de qué tipos pueden ser los algoritmos

    def __str__(self):
        return self.name

class Evaluation(models.Model):
    # INFO: una evaluacion no debería tener recomendaciones que le ha gustado al participante
    algorithm = models.ForeignKey('Algorithm', on_delete=models.CASCADE, null=False)
    #game = models.ForeignKey('Game', on_delete=models.CASCADE, null=False)
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    puntuation = models.FloatField()
    date_created = models.DateTimeField(auto_now_add=True)
    #results = models.TextField()
    #metrics = models.JSONField(default=list)

    def __str__(self):
        return f"Evaluation by {self.user} from recommendation {self.recommendation}"

class Preference(models.Model):
    text = models.ForeignKey('Game', on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    value = models.FloatField(default=0.0) 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user} - {self.category}"

