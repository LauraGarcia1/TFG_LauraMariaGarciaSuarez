from django.contrib import admin
from .models import Choice, Participant, Interaction, Questionnarie, Question, Answer, Recommendation, Game, Algorithm, Evaluation, Preference

# Register your models here.

# Participant model
@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'location', 'age', 'frequencyGame', 'expertiseGame', 'gender', 'date_created']
    search_fields = ['username', 'email']
    list_filter = ['gender', 'frequencyGame', 'expertiseGame', 'date_created']

# Interaction model
@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['id_participant', 'id_game', 'type', 'comment', 'date_created']
    search_fields = ['id_participant__username', 'id_game__id_BGG', 'type', 'comment']
    list_filter = ['type', 'date_created']

# Questionnarie model
@admin.register(Questionnarie)
class QuestionnarieAdmin(admin.ModelAdmin):
    list_display = ['name', 'language', 'date_created']
    search_fields = ['name']
    list_filter = ['language', 'date_created']

# Question model
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id_questionnarie', 'question', 'type', 'language', 'date_created']
    search_fields = ['question', 'type']
    list_filter = ['type', 'language', 'date_created']

# Answer model
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id_question', 'answer', 'language', 'date_created']
    search_fields = ['answer']
    list_filter = ['language', 'date_created']

# Recommendation model
@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['id_algorithm', 'id_participant', 'date_created']
    search_fields = ['id_algorithm__name', 'id_game__id_BGG']
    list_filter = ['date_created']

# Game model
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['id_BGG']
    search_fields = ['id_BGG']

# Algorithm model
@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'type', 'description']
    search_fields = ['name', 'type']
    list_filter = ['type']

# Evaluation model
@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['id_algorithm', 'id_participant', 'puntuation', 'date_created']
    search_fields = ['id_algorithm__name', 'id_game__id_BGG', 'id_participant__username']
    list_filter = ['puntuation', 'date_created']

# Preference model
@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['preference', 'category', 'value', 'id_participant']
    search_fields = ['category']
    list_filter = ['value', 'id_participant']

# Choice model
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['id_question', 'text']
    search_fields = ['text']
    list_filter = ['id_question', 'text']

from django.contrib import admin
from .models import EvalAnswers, GameRecommended, Evaluation, Game

# EvalAnswers model
@admin.register(EvalAnswers)
class EvalAnswersAdmin(admin.ModelAdmin):
    list_display = ('id_evaluation', 'id_gamerecommended', 'interested', 'buyorrecommend', 'preference', 'influence', 'moreoptions')
    list_filter = ('interested', 'buyorrecommend', 'preference', 'influence')
    search_fields = ('id_evaluation__id', 'id_gamerecommended__id', 'moreoptions')
    list_per_page = 20
    raw_id_fields = ('id_evaluation', 'id_gamerecommended')

    def get_interested_display(self, obj):
        return obj.get_interested_display()
    get_interested_display.short_description = 'Interest Level'

    def get_buyorrecommend_display(self, obj):
        return obj.get_buyorrecommend_display()
    get_buyorrecommend_display.short_description = 'Buy or Recommend Probability'

    def get_influence_display(self, obj):
        return obj.get_influence_display()
    get_influence_display.short_description = 'Influence Factor'

    def moreoptions_preview(self, obj):
        return obj.moreoptions[:100]
    
    moreoptions_preview.short_description = 'More Options (Preview)'

    list_display += ('get_interested_display', 'get_buyorrecommend_display', 'get_influence_display', 'moreoptions_preview')

# GameRecommended model
@admin.register(GameRecommended)
class GameRecommendedAdmin(admin.ModelAdmin):
    list_display = ('id_recommendation', 'id_game')
    search_fields = ('id_recommendation__id', 'id_game__name') 
    list_filter = ('id_recommendation',)

    def __str__(self):
        return f"{self.id_recommendation} - {self.id_game}"
