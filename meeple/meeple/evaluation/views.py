from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.conf import settings
from .forms import SignUpForm
from django.db import connections
from django.utils.translation import gettext_lazy as _
from .models import Preference, Participant, Game, Questionnarie, Question, Answer, Choice, Evaluation, Algorithm, Recommendation,  GameRecommended, EvalAnswers
import json


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
                request.session['userid'] = user.id
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

            request.session['userid'] = user.id

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

        for pref in preferences:
            with connections['external_db'].cursor() as cursor:
                cursor.execute("SELECT GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories FROM (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc WHERE zgc.gameid = %s;", [pref])
                categories = cursor.fetchone()
            
            Preference.objects.create(preference=Game.objects.get_or_create(id_BGG=int(pref))[0], category=str(categories) , value=0, id_participant=Participant.objects.get(id=request.session['userid']))
        
        print(preferences)
        return redirect('user-home')

    zacatrus_games = get_preferences_games()

    return render(request, 'preferences.html', {'zacatrus_games' : zacatrus_games, 'MEDIA_URL' : settings.MEDIA_URL})


def get_preferences_games():
    with connections['external_db'].cursor() as cursor:
        '''
        SELECT zg.id, zg.name, zg.url, zgd.description, GROUP_CONCAT( DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories, TRUNCATE(AVG(zr.rating), 1) AS ratings, GROUP_CONCAT( DISTINCT zgt.name ORDER BY zgt.name ASC) AS types, GROUP_CONCAT( DISTINCT zgct.name ORDER BY zgct.name ASC) AS contexts FROM (SELECT id, name, url FROM zacatrus_games LIMIT 10) zg LEFT JOIN zacatrus_game_descriptions zgd ON zg.id = zgd.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc ON zg.id = zgc.gameid LEFT JOIN (SELECT DISTINCT gameid, rating FROM zacatrus_ratings) zr ON zg.id = zr.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_types) zgt ON zg.id = zgt.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_contexts) zgct ON zg.id = zgct.gameid GROUP BY zg.id, zg.name, zg.url, zgd.description;
        '''
        # TODO: meter la consulta en otro lado, y no hardcoreado
        cursor.execute("SELECT id, name FROM zacatrus_games LIMIT 10;")
        zacatrus_games = cursor.fetchall()

        return zacatrus_games

def get_data_game(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        with connections['external_db'].cursor() as cursor:
            cursor.execute('SELECT zg.name, zgd.description, GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories, TRUNCATE(AVG (zr.rating), 1) AS ratings, GROUP_CONCAT(DISTINCT zgt.name ORDER BY zgt.name ASC) AS types, GROUP_CONCAT(DISTINCT zgct.name ORDER BY zgct.name ASC) AS contexts FROM zacatrus_games zg LEFT JOIN zacatrus_game_descriptions zgd ON zg.id = zgd.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc ON zg.id = zgc.gameid LEFT JOIN (SELECT DISTINCT gameid, rating FROM zacatrus_ratings) zr ON zg.id = zr.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_types) zgt ON zg.id = zgt.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_contexts) zgct ON zg.id = zgct.gameid WHERE zg.id = %s GROUP BY zg.name, zgd.description;', [id])
            result = cursor.fetchone()

            if result:
                return JsonResponse({'name': result[0], 'description': result[1], 'categories': result[2], 'ratings': result[3], 'types': result[4], 'contexts': result[5]})
            else:
                return JsonResponse({'error': 'No se encontraron datos'})

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
            return redirect(reverse('questionnarie'))
            #return redirect(reverse('first'))

        return redirect(reverse('home'))
    
    zacatrus_games = get_preferences_games()

    return render(request, 'recommendations.html', {'zacatrus_games' : zacatrus_games, 'MEDIA_URL' : settings.MEDIA_URL})


def questions(request):
    """
        Función que muestra la página de preguntas

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "newrecommendation":
            return redirect(reverse('newrecomm'))

        if request.path == "/questions/2":
            return render(request, 'question-two.html')
        elif request.path == "/questions/3":
            return render(request, 'question-three.html')

    if request.path == "/questions/1":
        return render(request, 'question-one.html')

    return render(request, 'recommendations.html')

def questionnarie(request):
    """
        Función que muestra la página del cuestionario

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "newrecommendation":
            selections = json.loads(request.POST.get('selections', '{}'))
            
            answers = []
            for question_id, choice_ids in selections.items():
                # Guardamos las respuestas del participante
                question = Question.objects.get(id=question_id)
                for choice in choice_ids:
                    answer = Answer.objects.create(id_question=question, answer=Choice.objects.get(id=choice))
                    # TODO: texto o id
                    answers.append(answer.answer.text)

            request.session['answers'] = answers
            return redirect('newrecomm')
    
    questions = get_data_questions()

    return render(request, 'questionnarie.html', {'list_questions' : questions})

def get_data_questions():
    # TODO: como hago con los cuestionarios
    questionnarie = Questionnarie.objects.first()
    questions = questionnarie.questions.all()

    questions_and_choices = {
        question: question.choices.all() for question in questions
    }

    return questions_and_choices

def newRecomm(request, answers = None):
    if request.method == "POST":
        responses = json.loads(request.POST.get('responses', '{}'))

        # TODO: como obtengo la puntuacion
        puntuation = 5
        evaluation = Evaluation.objects.create(id_algorithm=Algorithm.objects.get(id=1), id_participant=Participant.get(id=request.session['userid']), puntuation=puntuation, results="", metrics=[])

        for id_game, list_values in responses:
            EvalAnswers.objects.create(id_evaluation=evaluation, id_gamerecommended=GameRecommended.objects.get(id_recommendation=request.session['recommendation'], id_game=game), interested=list_values[0], buyrrecommend=list_values[1], preference=list_values[2], moreoptions=list_values[3], influence=list_values[4])
        
        if request.POST.get("button") == "exit":
            return redirect(reverse('recommendations'))
        elif request.POST.get("button") == "moreEvals":
            return redirect(reverse('first'))
        
    answers = request.session.get('answers', [])
    request.session.pop('answers', None)

    request.session['recommendation'] = Recommendation.objects.create(id_algorithm=Algorithm.objects.first(), id_participant=Participant.objects.get(id=request.session['userid'])).add_metrics(answers)

    # TODO: Generar los juegos de recomendación desde las respuestas
    zacatrus_games = get_preferences_games()
    for game in zacatrus_games:
        GameRecommended.objects.create(id_recommendation=request.session['recommendation'], id_game=Game.objects.get(id_BGG=game[0]))
    # TODO: Guardar datos del algoritmo

    return render(request, 'newrecommendations.html', {'zacatrus_games' : zacatrus_games, 'MEDIA_URL' : settings.MEDIA_URL, 'preferences_part' : answers})




# TODO: quitar esto

def prueba(request):
    return render(request, 'prueba.html')
