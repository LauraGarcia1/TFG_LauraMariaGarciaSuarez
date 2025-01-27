from django.urls import path, include
from . import views

urlpatterns = [
    
    path('', views.home, name='home'),
    path('signup/', views.signup, name='register'),
    path('logout/', views.logout, name='logout'),
    path('signup/preferences/', views.preferences, name='preferences'),
    path('my-recommendations/', views.recommendPage, name='my-recommendations'),
    path('my-studies/', views.StudiesView.as_view(), name='my-studies'),
    path('my-studies/create/', views.create_study, name='create-questionnarie'), 
    path('my-studies/<int:pk>/edit/', views.EditStudyView.as_view(), name='edit-study'),
    path('questionnaries/', views.questionnaries, name='list-questionnaries'),
    path('questions/', views.questionnarie, name='questionnarie'),
    path('new-recommendations/', views.newRecomm, name='newrecomm'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('get_data_game/', views.get_data_game, name='get_data_game'),


    path('prueba/', views.prueba, name='prueba'),
]