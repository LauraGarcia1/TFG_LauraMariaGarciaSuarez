"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene los forms del administrador del proyecto evaluation
"""
from django.contrib import admin
import nested_admin
from .models import Choice, Creator, Participant, User, Questionnaire, Question, Answer, Recommendation, Game, Algorithm, Evaluation, Preference, Section

class ChoiceInline(nested_admin.NestedTabularInline):
    """Clase para manejar la visualización anidada de opciones en el panel de administración.

    Args:
        nested_admin (NestedTabularInline): permite crear inlines anidados en la administración de Django con un diseño tabular.
    """
    model = Choice
    extra = 1  # Número de opciones adicionales por defecto

class QuestionInline(nested_admin.NestedTabularInline):
    """Clase para manejar la visualización anidada de preguntas en el panel de administración.

    Args:
        nested_admin (NestedTabularInline): permite crear inlines anidados en la administración de Django con un diseño tabular.
    """
    model = Question
    inlines = [ChoiceInline]
    extra = 1

class SectionInline(nested_admin.NestedStackedInline):
    """Clase para manejar la visualización anidada de secciones en el panel de administración.

    Args:
        nested_admin (NestedTabularInline): permite crear inlines anidados en la administración de Django con un diseño tabular.
    """
    model = Section
    inlines = [QuestionInline]
    extra = 1 # Número de secciones adicionales por defecto

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Administra la interfaz de usuario en el panel de administración de Django.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['username', 'email', 'location', 'birthdate', 'date_created', 'rol']
    search_fields = ['username', 'email']
    list_filter = ['date_created']

@admin.register(Creator)
class CreatorAdmin(UserAdmin):
    """Administra la interfaz de usuario de tipo Creador en el panel de administración de Django.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    fieldsets = UserAdmin.fieldsets
    list_display = ('username', 'email', 'location', 'date_created')
    search_fields = ('username', 'email')

@admin.register(Participant)
class ParticipantAdmin(UserAdmin):
    """Administra la interfaz de usuario de tipo Participante en el panel de administración de Django.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    fieldsets = (
        ("User Info", {"fields": ("username", "email", "password")}),
        ("Additional Info", {"fields": ("rol", "gender", "frequencyGame", "expertiseGame")}),
    )

    list_display = ('username', 'email', 'gender', 'frequencyGame', 'expertiseGame', 'date_created')
    search_fields = ('username', 'email')

@admin.register(Questionnaire)
class QuestionnaireAdmin(nested_admin.NestedModelAdmin):
    """Clase para gestionar el modelo Questionnaire en el panel de administración.

    Args:
        nested_admin (NestedTabularInline): permite crear inlines anidados en la administración de Django con un diseño tabular.
    """
    inlines = [SectionInline]
    list_display = ['name', 'language', 'date_created']
    search_fields = ['name']
    list_filter = ['language', 'date_created']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Question en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['section', 'question_text', 'type', 'language', 'date_created']
    search_fields = ['question_text', 'type']
    list_filter = ['type', 'language', 'date_created']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Answer en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['question', 'choice', 'language', 'date_created']
    search_fields = ['answer']
    list_filter = ['language', 'date_created']

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Recommendation en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['algorithm', 'game', 'date_created']
    search_fields = ['algorithm__name', 'game__id_BGG']
    list_filter = ['date_created']

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Game en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['id_BGG']
    search_fields = ['id_BGG']

@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Algorithm en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['name', 'version', 'type', 'description']
    search_fields = ['name', 'type']
    list_filter = ['type']

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Evaluation en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['user', 'answers', 'date_created']
    search_fields = ['game__id_BGG', 'user__username']
    list_filter = ['answers', 'date_created']

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Preference en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['text', 'category', 'value', 'user']
    search_fields = ['category']
    list_filter = ['value', 'user']

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Choice en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    list_display = ['question', 'choice_text']
    search_fields = ['choice_text']
    list_filter = ['question', 'choice_text']

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Clase para gestionar el modelo Section en el panel de administración.

    Args:
        admin (ModelAdmin): Clase base que permite personalizar la visualización y gestión de un modelo en el panel de administración de Django.
    """
    inlines = [QuestionInline]
    list_display = ('title', 'questionnaire')
    search_fields = ('title', 'questionnaire')
    list_filter = ('questionnaire',)

    def __str__(self):
        return f"{self.questionnaire} - {self.title}"

