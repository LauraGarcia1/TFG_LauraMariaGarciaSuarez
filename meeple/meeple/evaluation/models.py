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
        return f"Username: {self.username}"

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
    evaluation = models.ForeignKey('Evaluation', on_delete=models.CASCADE, null=False, related_name='interactions')
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE, null=False)
    interested = models.IntegerField(choices=INTEREST_CHOICES, default=3)
    buyorrecommend = models.IntegerField(choices=GENERAL_CHOICES, default=3)
    preference = models.BooleanField(default=False)
    # TODO: TextField??
    moreoptions = models.TextField()
    influences = models.JSONField(default=list)

    def __str__(self):
        return f"Evaluation for"
    
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

class Algorithm(models.Model):
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
        return f"Algorithm name: {self.name}"

class Questionnaire(models.Model):
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

    # Método para comprobar si los campos están rellenos
    def are_fields_filled(self):
        return bool(self.description and self.name and self.algorithm and self.language)

    def __str__(self):
        return f"Questionnaire name: {self.name}\nQuestionnaire id: {self.id}"

class Section(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, related_name='sections', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True, blank=True)

    # Método para comprobar si los campos están rellenos
    def are_fields_filled(self):
        return bool(self.title)

    def __str__(self):
        return f"Section title: {self.title}\nSection id: {self.id}"

class Question(models.Model):
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
        ordering = ['date_created']

    # Método para comprobar si los campos están rellenos
    def are_fields_filled(self):
        return bool(self.type and self.language and self.question_text)
    
    def __str__(self):
        return f"Question text: {self.question_text}\nQuestion id: {self.id}"
    
    

class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True, related_name='choices')
    choice_text = models.CharField(max_length=50, blank=True, null=True)

    # Método para comprobar si los campos están rellenos
    def are_fields_filled(self):
        return bool(self.choice_text)

    def __str__(self):
        return f"Choice text: {self.choice_text}"
    

class Answer(models.Model):
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
        ordering = ['date_created']

    def __str__(self):
        return f"Answer choice: {self.choice}\nAnswer text: {self.text}\nAnswer id: {self.id}"

class Recommendation(models.Model):
    algorithm = models.ForeignKey('Algorithm', on_delete=models.CASCADE, null=False)
    game = models.ForeignKey('Game', on_delete=models.SET_NULL, null=True)
    metrics = models.JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation algorithm: {self.algorithm}\nRecommendation game: {self.game}\nRecommendation metrics: {self.metrics}\nRecommendation id: {self.id}"
    
    def add_metrics(self, new_metrics):
        self.metrics.extend(new_metrics)
        self.save()

class Game(models.Model):
    id_BGG = models.IntegerField(default=0)

    def __str__(self):
        return f"Game id: {self.id}\nBGG id: {self.id_BGG}"

class Evaluation(models.Model):
    recommendation = models.ForeignKey('Recommendation', on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    answers = models.JSONField(default=list)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation user: {self.user}\nEvaluation recommendation: {self.recommendation}\nEvaluation id: {self.id}"

class Preference(models.Model):
    text = models.ForeignKey('Game', on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    value = models.FloatField(default=0.0) # TODO: Es necesario?
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Preference user: {self.user}\nPreference categories: {self.category}\nPreference id: {self.id}"

