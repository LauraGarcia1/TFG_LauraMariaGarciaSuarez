from django.urls import path, include
from .views import (
    home, signup, logout, preferences, recommendPage, StudiesView, create_study, EditStudyView, delete_section, questionnaries, questionnarie, newRecomm, get_data_game, prueba, QuestionnarieCreate, QuestionnarieUpdate, create_section_ajax
)

urlpatterns = [
    
    path('', home, name='home'),
    path('signup/', signup, name='register'),
    path('logout/', logout, name='logout'),
    path('signup/preferences/', preferences, name='preferences'),
    path('my-recommendations/', recommendPage, name='my-recommendations'),
    path('my-studies/', StudiesView.as_view(), name='my-studies'),
    path('my-studies/create/', create_study, name='create-questionnarie'), 
    path('my-studies/<int:pk>/edit/', QuestionnarieUpdate.as_view(), name='edit-questionnarie'),
    path("create-section/", create_section_ajax, name="create_section_ajax"),
    path('delete-section/<int:pk>/', delete_section, name='delete-section'),
    path('questionnaries/', questionnaries, name='list-questionnaries'),
    path('questions/', questionnarie, name='questionnarie'),
    path('new-recommendations/', newRecomm, name='newrecomm'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('get_data_game/', get_data_game, name='get_data_game'),


    path('prueba/', prueba, name='prueba'),
]