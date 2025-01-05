from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate

from django.conf import settings
from .forms import SignUpForm
from django.db import connections
from django.utils.translation import gettext_lazy as _


def home(request):
    """
        Función que muestra la página de inicio

        Autor: Laura Mª García Suárez
    """
    username = request.POST.get("username")
    password = request.POST.get("password")

    if request.method == "POST":
        if request.POST.get("button") == "signup":
            request.session['username'] = username
            request.session['password'] = password
            return redirect(reverse('register'))
        if request.POST.get("button") == "signin":
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse('user-home'))

    title_home = _("Welcome")
    username_home = _("Username")
    password_home = _("Password")
    login_home = _("Login")
    signup_home = _("Sign up")

    return render(request, 'home.html', {'title': title_home, 'username': username_home, 'password': password_home, 'login': login_home, 'signup': signup_home, 'redirect_to': request.path})


def signup(request):
    """
        Función que muestra la página de registro

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        form = SignUpForm(request.POST)

        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        location = request.POST.get("location")
        age = request.POST.get("age")
        frequencyGame = request.POST.get("frequencyGame")
        expertiseGame = request.POST.get("expertiseGame")
        gender = request.POST.get("gender")

        print(form.errors)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password, email=email, location=location, age=age, frequencyGame=frequencyGame, expertiseGame=expertiseGame, gender=gender)

            if user is not None:
                login(request, user)
                return redirect('preferences')
        else:
            print(form.errors)
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'username': request.session['username'], 'password': request.session['password'], 'form': form})


def preferences(request):
    if request.method == "POST":
        preferences = request.POST.getlist('likedPreferences')

        print(preferences)
        return redirect('user-home')

    zacatrus_games = get_data()

    return render(request, 'preferences.html', {'zacatrus_games' : zacatrus_games, 'MEDIA_URL' : settings.MEDIA_URL})


def get_data():
    with connections['external_db'].cursor() as cursor:
        '''
        SELECT zg.id, zg.name, zg.url, zgd.description, GROUP_CONCAT( DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories, TRUNCATE(AVG(zr.rating), 1) AS ratings, GROUP_CONCAT( DISTINCT zgt.name ORDER BY zgt.name ASC) AS types, GROUP_CONCAT( DISTINCT zgct.name ORDER BY zgct.name ASC) AS contexts FROM (SELECT id, name, url FROM zacatrus_games LIMIT 10) zg LEFT JOIN zacatrus_game_descriptions zgd ON zg.id = zgd.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc ON zg.id = zgc.gameid LEFT JOIN (SELECT DISTINCT gameid, rating FROM zacatrus_ratings) zr ON zg.id = zr.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_types) zgt ON zg.id = zgt.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_contexts) zgct ON zg.id = zgct.gameid GROUP BY zg.id, zg.name, zg.url, zgd.description;
        '''
        # TODO: meter la consulta en otro lado, y no hardcoreado
        cursor.execute(
            "SELECT zg.id, zg.name FROM (SELECT id, name, url FROM zacatrus_games LIMIT 10) zg;")
        zacatrus_games = cursor.fetchall()

        print(zacatrus_games)

        return zacatrus_games


def userHome(request):
    """
        Función que muestra la página principal del usuario

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "recommendations":
            return redirect(reverse('recommendations'))

        return redirect(reverse('home'))

    return render(request, 'userhomepage.html')


def recommendPage(request):
    """
        Función que muestra la página de recomendaciones

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "newrecommendation":
            return redirect(reverse('first'))

        return redirect(reverse('home'))
    
    zacatrus_games = get_data()

    return render(request, 'recommendations.html', {'zacatrus_games' : zacatrus_games, 'MEDIA_URL' : settings.MEDIA_URL})


def questions(request):
    """
        Función que muestra la página de recomendaciones

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        print(request.path, request.path == "/questions/3")
        if request.POST.get("button") == "newrecommendation":
            return redirect(reverse('newrecomm'))

        if request.path == "/questions/2":
            return render(request, 'question-two.html')
        elif request.path == "/questions/3":
            return render(request, 'question-three.html')

    if request.path == "/questions/1":
        return render(request, 'question-one.html')

    return render(request, 'recommendations.html')


def newRecomm(request):
    if request.method == "POST":
        recommendations = request.POST.getlist('likedRecommendations')

        print(recommendations)
        if request.POST.get("button") == "exit":
            return redirect(reverse('recommendations'))
        elif request.POST.get("button") == "moreEvals":
            return redirect(reverse('first'))
    
    zacatrus_games = get_data()

    return render(request, 'newrecommendations.html', {'zacatrus_games' : zacatrus_games, 'MEDIA_URL' : settings.MEDIA_URL})

# TODO: quitar esto


def prueba(request):
    return render(request, 'prueba.html')
