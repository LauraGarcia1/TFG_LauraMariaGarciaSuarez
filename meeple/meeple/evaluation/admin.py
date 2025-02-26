from django.contrib import admin
import nested_admin
from .models import Choice, User, Interaction, Questionnaire, Question, Answer, Recommendation, Game, Algorithm, Evaluation, Preference, GameRecommended, Section

    # Inline para Choices dentro de Questions
class ChoiceInline(nested_admin.NestedTabularInline):
    model = Choice
    extra = 1  # Número de opciones adicionales por defecto

# Inline para Questions dentro de Sections
class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 1

# Inline para Sections dentro de Questionnaire
class SectionInline(nested_admin.NestedStackedInline):
    model = Section
    inlines = [QuestionInline]
    extra = 1

# User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'rol', 'location', 'age', 'frequencyGame', 'expertiseGame', 'gender', 'date_created']
    search_fields = ['username', 'email']
    list_filter = ['gender', 'frequencyGame', 'expertiseGame', 'date_created']

# Questionnaire model
@admin.register(Questionnaire)
class QuestionnaireAdmin(nested_admin.NestedModelAdmin):
    inlines = [SectionInline]
    list_display = ['name', 'language', 'date_created']
    search_fields = ['name']
    list_filter = ['language', 'date_created']

# Question model
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['section', 'question_text', 'type', 'language', 'date_created']
    search_fields = ['question_text', 'type']
    list_filter = ['type', 'language', 'date_created']

# Answer model
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice', 'language', 'date_created']
    search_fields = ['answer']
    list_filter = ['language', 'date_created']

# Recommendation model
@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['algorithm', 'user', 'date_created']
    search_fields = ['algorithm__name', 'game__id_BGG']
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
    list_display = ['algorithm', 'user', 'puntuation', 'date_created']
    search_fields = ['algorithm__name', 'game__id_BGG', 'user__username']
    list_filter = ['puntuation', 'date_created']

# Preference model
@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['text', 'category', 'value', 'user']
    search_fields = ['category']
    list_filter = ['value', 'user']

# Choice model
@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'choice_text']
    search_fields = ['choice_text']
    list_filter = ['question', 'choice_text']

# Interaction model
@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'gamerecommended', 'interested', 'buyorrecommend', 'preference', 'influences', 'moreoptions')
    list_filter = ('interested', 'buyorrecommend', 'preference', 'influences')
    search_fields = ('evaluation__id', 'gamerecommended__id', 'moreoptions')
    list_per_page = 20
    raw_fields = ('evaluation', 'gamerecommended')

    def get_interested_display(self, obj):
        return obj.get_interested_display()
    get_interested_display.short_description = 'Interest Level'

    def get_buyorrecommend_display(self, obj):
        return obj.get_buyorrecommend_display()
    get_buyorrecommend_display.short_description = 'Buy or Recommend Probability'

    def influences_display(self, obj):
        INFLUENCE_CHOICES = {
            '1': 'Price',
            '2': 'Quality',
            '3': 'Features',
            '4': 'Popularity',
            '5': 'Recommendations from other users',
            '6': 'Other'
        }
        return [INFLUENCE_CHOICES.get(i, 'Unknown') for i in obj.influences]

    def moreoptions_preview(self, obj):
        return obj.moreoptions[:100]
    
    moreoptions_preview.short_description = 'More Options (Preview)'

    list_display += ('get_interested_display', 'get_buyorrecommend_display', 'influences_display', 'moreoptions_preview')

# GameRecommended model
@admin.register(GameRecommended)
class GameRecommendedAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'game')
    search_fields = ('recommendation__id', 'game__name') 
    list_filter = ('recommendation',)

    def __str__(self):
        return f"{self.recommendation} - {self.game}"

# GameRecommended model
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'questionnaire')
    search_fields = ('title', 'questionnaire')
    list_filter = ('questionnaire',)

    def __str__(self):
        return f"{self.questionnaire} - {self.title}"

