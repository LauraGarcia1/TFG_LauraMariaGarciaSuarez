"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene las rutas disponibles del proyecto evaluation
"""
from django.urls import path, include
from .views import (
    home, signup, logout, preferences, recommendPage, StudiesView, create_study, edit_study, questionnaires, view_questionnaire, get_data_game, delete_study, upload_study, view_study, algorithms
)

urlpatterns = [
    
    path('', home, name='home'),
    path('signup/', signup, name='register'),
    path('logout/', logout, name='logout'),
    path('signup/preferences/', preferences, name='preferences'),
    path('my-recommendations/', recommendPage, name='my-recommendations'),
    path('my-studies/', StudiesView.as_view(), name='my-studies'),
    path('my-studies/algorithms/', algorithms, name='list-algorithms'), 
    path('my-studies/create/', create_study, name='create-questionnaire'), 
    path('my-studies/<int:pk>/edit/', edit_study, name='edit-questionnaire'),
    path('my-studies/<int:pk>/view/', view_study, name='view-questionnaire'),
    path('my-studies/<int:pk>/delete/', delete_study, name='delete-questionnaire'),
    path('my-studies/<int:pk>/upload/', upload_study, name='upload-questionnaire'),
    path('questionnaires/', questionnaires, name='list-questionnaires'),
    path('questions/<int:pk>/', view_questionnaire, name='questionnaire'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('get_data_game/', get_data_game, name='get_data_game'),
]