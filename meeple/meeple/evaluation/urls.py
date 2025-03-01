from django.urls import path, include
from .views import (
    home, signup, logout, preferences, recommendPage, StudiesView, create_study, edit_study, delete_section, questionnaires, view_questionnaire, newRecomm, get_data_game, prueba, create_section_ajax, delete_study, upload_study, view_study
)

urlpatterns = [
    
    path('', home, name='home'),
    path('signup/', signup, name='register'),
    path('logout/', logout, name='logout'),
    path('signup/preferences/', preferences, name='preferences'),
    path('my-recommendations/', recommendPage, name='my-recommendations'),
    path('my-studies/', StudiesView.as_view(), name='my-studies'),
    path('my-studies/create/', create_study, name='create-questionnaire'), 
    path('my-studies/<int:pk>/edit/', edit_study, name='edit-questionnaire'),
    path('my-studies/<int:pk>/view/', view_study, name='view-questionnaire'),
    path('my-studies/<int:pk>/delete/', delete_study, name='delete-questionnaire'),
    path('my-studies/<int:pk>/upload/', upload_study, name='upload-questionnaire'),
    path("create-section/", create_section_ajax, name="create_section_ajax"),
    path('delete-section/<int:pk>/', delete_section, name='delete-section'),
    path('questionnaires/', questionnaires, name='list-questionnaires'),
    path('questions/<int:pk>/', view_questionnaire, name='questionnaire'),
    path('new-recommendations/', newRecomm, name='newrecomm'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('get_data_game/', get_data_game, name='get_data_game'),


    path('prueba/', prueba, name='prueba'),
]