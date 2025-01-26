from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.conf import settings
from django.db import connections
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic import UpdateView
from django.utils.translation import gettext_lazy as _
from .forms import SignUpForm, QuestionnarieForm
from .models import Preference, User, Game, Questionnarie, Question, Answer, Choice, Evaluation, Algorithm, Recommendation,  GameRecommended, Interaction
import json

def home(request):
    """
        Función que muestra la página de inicio

        Autor: Laura Mª García Suárez
    """
    username = request.POST.get("username")
    password = request.POST.get("password")

    if request.method == "POST":
        if request.POST.get("button") == "signin":
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['userid'] = user.id
                if user.rol == "ER":
                    return redirect(reverse('my-studies'))
                return redirect(reverse('my-recommendations'))
        request.session['username'] = username
        request.session['password'] = password
        
        return redirect(reverse('register'))

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
        gender = request.POST.get("gender")
        rol = request.POST.get("rol")
        frequencyGame = request.POST.get("frequencyGame")
        expertiseGame = request.POST.get("expertiseGame")

        print(form.errors)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password, email=email, location=location,
                                age=age, rol=rol, frequencyGame=frequencyGame, expertiseGame=expertiseGame, gender=gender)

            request.session['userid'] = user.id
            request.session['rol'] = user.rol

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
                cursor.execute(
                    "SELECT GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories FROM (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc WHERE zgc.gameid = %s;", [pref])
                categories = cursor.fetchone()

            Preference.objects.create(preference=Game.objects.get_or_create(id_BGG=int(pref))[0], category=str(
                categories), value=0, id_user=User.objects.get(id=request.session.get('userid')))

        if request.session.get('rol') == "ER":
            return redirect(reverse('my-studies'))
        return redirect(reverse('my-recommendations'))

    zacatrus_games = get_preferences_games()

    return render(request, 'preferences.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL})


def get_preferences_games():
    with connections['external_db'].cursor() as cursor:
        ''' TODO: eliminar esta consulta
        SELECT zg.id, zg.name, zg.url, zgd.description, GROUP_CONCAT( DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories, TRUNCATE(AVG(zr.rating), 1) AS ratings, GROUP_CONCAT( DISTINCT zgt.name ORDER BY zgt.name ASC) AS types, GROUP_CONCAT( DISTINCT zgct.name ORDER BY zgct.name ASC) AS contexts FROM (SELECT id, name, url FROM zacatrus_games LIMIT 10) zg LEFT JOIN zacatrus_game_descriptions zgd ON zg.id = zgd.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc ON zg.id = zgc.gameid LEFT JOIN (SELECT DISTINCT gameid, rating FROM zacatrus_ratings) zr ON zg.id = zr.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_types) zgt ON zg.id = zgt.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_contexts) zgct ON zg.id = zgct.gameid GROUP BY zg.id, zg.name, zg.url, zgd.description;
        '''
        cursor.execute("SELECT id, name FROM zacatrus_games LIMIT 5;")
        zacatrus_games = cursor.fetchall()

        return zacatrus_games


def get_data_game(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        with connections['external_db'].cursor() as cursor:
            cursor.execute(
                'SELECT zg.name, zgd.description, GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories, TRUNCATE(AVG (zr.rating), 1) AS ratings, GROUP_CONCAT(DISTINCT zgt.name ORDER BY zgt.name ASC) AS types, GROUP_CONCAT(DISTINCT zgct.name ORDER BY zgct.name ASC) AS contexts FROM zacatrus_games zg LEFT JOIN zacatrus_game_descriptions zgd ON zg.id = zgd.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc ON zg.id = zgc.gameid LEFT JOIN (SELECT DISTINCT gameid, rating FROM zacatrus_ratings) zr ON zg.id = zr.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_types) zgt ON zg.id = zgt.gameid LEFT JOIN (SELECT DISTINCT gameid, name FROM zacatrus_game_contexts) zgct ON zg.id = zgct.gameid WHERE zg.id = %s GROUP BY zg.name, zgd.description;', [id])
            result = cursor.fetchone()

            if result:
                return JsonResponse({'name': result[0], 'description': result[1], 'categories': result[2], 'ratings': result[3], 'types': result[4], 'contexts': result[5]})
            else:
                return JsonResponse({'error': 'No se encontraron datos'})


def questionnaries(request):
    """
        Función que muestra la página principal del usuario

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "recommendations":
            return redirect(reverse('questionnarie'))

        return redirect(reverse('home'))
    
    questionnaries = Questionnarie.objects.get_queryset()

    return render(request, 'liststudies.html', {'questionnaries' : questionnaries})

class StudiesView(ListView):
    """
        Función que muestra la página principal del usuario con rol Evaluador.

        Autor: Laura Mª García Suárez
    """
    model = Questionnarie
    template_name = 'mystudies.html'
    context_object_name = 'studies'

    def get_queryset(self):
        # Filtrar los cuestionarios por el usuario autenticado
        if self.request.user.is_authenticated:
            return Questionnarie.objects.filter(id_user=self.request.user)
        return Questionnarie.objects.none()

class QuestionnarieCreateView(CreateView):
    """
    Vista que permite crear un nuevo cuestionario.
    """
    model = Questionnarie
    template_name = 'createstudy.html'
    fields = ['name', 'description', 'language']

    success_url = reverse_lazy('my-studies')

    def form_valid(self, form):
        form.instance.id_user = self.request.user
        return super().form_valid(form)
    
class EditStudyView(UpdateView):
    model = Questionnarie
    form_class = QuestionnarieForm
    template_name = 'editstudy.html'
    success_url = '/studies/'


def recommendPage(request):
    """
        Función que muestra la página de recomendaciones

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "newrecommendation":
            return redirect(reverse('list-questionnaries'))
            # return redirect(reverse('first'))

        return redirect(reverse('home'))

    zacatrus_games = get_preferences_games()

    return render(request, 'myrecommendations.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL})


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

    return render(request, 'liststudies.html')


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
                    answer = Answer.objects.create(id_question=question, answer=Choice.objects.get(id=choice), id_user=User.objects.get(id=request.session.get('userid')), language=settings.LANGUAGE_CODE)
                    answers.append(answer.answer.choice)

            request.session['answers'] = answers
            return redirect('newrecomm')

    questions = get_data_questions()

    return render(request, 'questionnarie.html', {'list_questions': questions})


def get_data_questions():
    """
        Función que obtiene las opciones de las preguntas

        Autor: Laura Mª García Suárez
    """

    # TODO: como hago con los cuestionarios
    questionnarie = Questionnarie.objects.first()
    questions = questionnarie.questions.all()

    questions_and_choices = {
        question: question.choices.all() for question in questions
    }

    return questions_and_choices


def newRecomm(request, answers=None):
    """
        Función que muestra la página de las recomendaciones

        Autor: Laura Mª García Suárez
    """
    
    answers = request.session.get('answers', [])
    request.session.pop('answers', None)

    zacatrus_games = get_preferences_games()

    if request.method == "POST":
        selections = json.loads(request.POST.get('selections', '{}'))

        # TODO: como obtengo la puntuacion
        puntuation = 5
        evaluation = Evaluation.objects.create(id_algorithm=Algorithm.objects.get(id=1), id_recommendation=Recommendation.objects.get(
            id=request.session.get('recommendation')), id_user=User.objects.get(id=request.session.get('userid')), puntuation=puntuation)

        print(selections)
        for id_game, list_values in selections.items():
            print(list_values)
            interaction = Interaction.objects.create(id_evaluation=evaluation, id_gamerecommended=GameRecommended.objects.get(id_recommendation=request.session['recommendation'], id_game=Game.objects.get(
                id_BGG=int(id_game))), interested=list_values["firstquestion"], buyorrecommend=list_values["secondquestion"], preference=list_values["thirdquestion"], moreoptions=list_values["fourthquestion"])
            interaction.add_influences(list_values["fifthquestion"])

        if request.POST.get("button") == "exit":
            request.session.pop('recommendation', None)
            return redirect(reverse('list-questionnaries'))
        elif request.POST.get("button") == "moreEvals":
            request.session.pop('recommendation', None)
            # TODO: Guardar zacatrus_games?
            return render(request, 'newrecommendations.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL, 'preferences_part': answers})

    recommendation = Recommendation.objects.create(id_algorithm=Algorithm.objects.first(
    ), id_user=User.objects.get(id=request.session['userid']))
    recommendation.add_metrics(answers)

    request.session['recommendation'] = recommendation.id

    # TODO: Generar los juegos de recomendación desde las respuestas
    for game in zacatrus_games:
        GameRecommended.objects.create(id_recommendation=Recommendation.objects.get(id=request.session.get(
            'recommendation')), id_game=Game.objects.get_or_create(id_BGG=int(game[0]))[0])
    # TODO: Guardar datos del algoritmo

    return render(request, 'newrecommendations.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL, 'preferences_part': answers})


# TODO: quitar esto

def prueba(request):
    return render(request, 'prueba.html')
