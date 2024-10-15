from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='register'),
    path('signup/preferences/', views.preferences, name='preferences'),
    path('recommendations/', views.recommendPage, name='recommendations'),
    path('userhome/', views.userHome, name='user-home'),
    path('questions/1', views.questions, name='first'),
    path('questions/2', views.questions, name='second'),
    path('questions/3', views.questions, name='third'),
]