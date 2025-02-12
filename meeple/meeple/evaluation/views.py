from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.db import connections, transaction
from django.views.generic.list import ListView
from django.views.generic import UpdateView, CreateView
from django.utils.translation import gettext_lazy as _
from .forms import SignUpForm, QuestionnarieForm, SectionFormSet, QuestionFormSet, ChoiceForm, ChoiceFormSet
from .models import Preference, User, Game, Questionnarie, Question, Answer, Choice, Evaluation, Algorithm, Recommendation,  GameRecommended, Interaction, Section
import json

def home(request):
    """
        Función que muestra la página de inicio

        Autor: Laura Mª García Suárez
    """
    title_home = _("Welcome")
    username_home = _("Username")
    password_home = _("Password")
    login_home = _("Login")
    signup_home = _("Sign up")

    if request.user.is_authenticated:
        if User.objects.get(id=request.session.get('userid')).rol == "ER":
            return redirect(reverse('my-studies'))
        redirect(reverse('my-recommendations'))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if request.POST.get("button") == "signin":
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['userid'] = user.id
                if user.rol == "ER":
                    return redirect(reverse('my-studies'))
                return redirect(reverse('my-recommendations'))
            
            if User.objects.filter(username=username).exists():
                return render(request, 'home.html', {'title': title_home, 'username': username_home, 'password': password_home, 'login': login_home, 'signup': signup_home, 'redirect_to': request.path})

        request.session['username'] = username
        request.session['password'] = password
        
        return redirect(reverse('register'))


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

def logout(request):
    request.session.flush()
    return redirect('home')
    

@login_required
def preferences(request):
    if request.method == "POST":
        preferences = request.POST.getlist('likedPreferences')

        for pref in preferences:
            with connections['external_db'].cursor() as cursor:
                cursor.execute(
                    "SELECT GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories FROM (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc WHERE zgc.gameid = %s;", [pref])
                categories = cursor.fetchone()

            Preference.objects.create(text=Game.objects.get_or_create(id_BGG=int(pref))[0], category=str(
                categories), value=0, user=User.objects.get(id=request.session.get('userid')))

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

@login_required
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

class StudiesView(LoginRequiredMixin, ListView):
    """
        Función que muestra la página principal del usuario con rol Evaluador.

        Autor: Laura Mª García Suárez
    """
    model = Questionnarie
    template_name = 'mystudies.html'
    context_object_name = 'questionnaries'

    def get_queryset(self):
        return Questionnarie.objects.filter(user=self.request.user)

class QuestionnarieInline():
    form_class = QuestionnarieForm
    model = Questionnarie
    template_name = 'createstudy.html'

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(forms=form))
        
        self.object = form.save()

        # Save objects
        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('my-studies')
    
    def formset_sections_valid(self, formset):
        """
        def formset_questions_valid(self, formset):
        """

        """
        questions = formset.save(commit=False)
        for question in questions:
            question.sect = self.object
            question.save()

        """
        sections = formset.save(commit=False)
        for section in sections:
            section.questionnarie = self.object
            section.save()

class QuestionnarieCreate(LoginRequiredMixin, QuestionnarieInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(QuestionnarieCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'sections': SectionFormSet(prefix='sections'),
            }
        else:
            return {
                'sections': SectionFormSet(self.request.POST or None, self.request.FILES or None, prefix='sections'),
            }
        
class QuestionnarieUpdate(LoginRequiredMixin, QuestionnarieInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(QuestionnarieUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()

    def get_named_formsets(self):
        return {
            'sections': SectionFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='sections'),
        }
    
def delete_section(request, pk):
    try:
        section = Section.objects.get(id=pk)
    except Section.DoesNotExist:
        messages.success(
            request, 'Object Does not exist'
        )
        return redirect('edit-questionnarie', pk=section.questionnarie.id)

@login_required
def create_study(request):
    if request.method == 'POST':
        print(request.POST)
        questionnaire_form = QuestionnarieForm(request.POST)
        #section_formset = SectionFormSet(request.POST)

        if questionnaire_form.is_valid():
        #if questionnaire_form.is_valid() and section_formset.is_valid():
            questionnaire = questionnaire_form.save(commit=False)
            questionnaire.user = User.objects.get(id=request.session.get('userid'))
            questionnaire.save()
        
            section_index = 0
            while True:
                section_title_key = f"sections-{section_index}-title"
                section_title = request.POST.get(section_title_key, "").strip()
                if not section_title:
                    # Si no se encuentra un título, asumimos que ya no hay más secciones
                    break

                # Crear la sección para este cuestionario
                section = Section.objects.create(
                    questionnarie=questionnaire,
                    title=section_title
                )
                # TODO: delete va a hacer que no sea así la función
                # Procesar las preguntas de esta sección
                question_index = 0
                while True:
                    question_key_prefix = f"questions-{section_index}-{question_index}"
                    question_keys = [value for key, value in request.POST.items() if key.startswith(question_key_prefix)]
                    print(question_keys)
                    if not question_keys:
                        # No se encontró más preguntas para esta sección
                        break
                    # Crear la pregunta para la sección
                    question = Question.objects.create(
                        section=section,
                        text=question_keys[0],
                        type=question_keys[1],
                        language=question_keys[2]
                    )
                    choice_index = 0
                    while True:
                        choice_text_key = f"choices-{section_index}-{question_index}-{choice_index}-text"
                        choice_keys = request.POST.get(choice_text_key, "").strip()
                        if not choice_keys:
                            # No se encontró más preguntas para esta sección
                            break
                        # Crear la pregunta para la sección
                        Choice.objects.create(
                            question=question,
                            text=choice_keys,
                        )
                        choice_index += 1
                    question_index += 1
                # Incrementamos el índice de sección y seguimos con la siguiente
                section_index += 1

            # Redireccionar o mostrar mensaje de éxito
            return redirect('my-studies')  # Reemplaza 'success_url' por tu ruta de éxito
    
    # Si es GET, simplemente mostramos el formulario vacío
    questionnaire_form = QuestionnarieForm()
    section_formset = SectionFormSet(queryset=Section.objects.none(), prefix='sections')
    question_formset = QuestionFormSet(prefix='questions')
    choice_formset = ChoiceFormSet(queryset=Choice.objects.none(), prefix='choices')

    print(section_formset)

    return render(request, 'createstudy.html', {
        'questionnarie_form': questionnaire_form,
        'section_formset': section_formset,
        'question_formset': question_formset,
        'choice_formset': choice_formset,
    })

def create_section_ajax(request):
    if request.method == "POST":
        title = request.POST.get("title", "")
        section = Section.objects.create(title=title)
        return JsonResponse({"id": section.id})
    
class EditStudyView(LoginRequiredMixin, UpdateView):
    model = Questionnarie
    form_class = QuestionnarieForm
    template_name = 'editstudy.html'
    success_url = reverse_lazy('my-studies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['section_formset'] = SectionFormSet(self.request.POST, instance=self.object)
        else:
            context['section_formset'] = SectionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        section_formset = context['section_formset']

        # Usar una transacción para guardar todo o nada
        with transaction.atomic():
            self.object = form.save()
            if section_formset.is_valid():
                sections = section_formset.save(commit=False)
                for section in sections:
                    section.questionnarie = self.object
                    section.save()
                section_formset.save_m2m()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)

@login_required
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

@login_required
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

@login_required
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
                    answer = Answer.objects.create(id_question=question, answer=Choice.objects.get(id=choice), user=User.objects.get(id=request.session.get('userid')), language=settings.LANGUAGE_CODE)
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

@login_required
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
        evaluation = Evaluation.objects.create(algorithm=Algorithm.objects.get(id=1), recommendation=Recommendation.objects.get(
            id=request.session.get('recommendation')), user=User.objects.get(id=request.session.get('userid')), puntuation=puntuation)

        print(selections)
        for id_game, list_values in selections.items():
            print(list_values)
            interaction = Interaction.objects.create(evaluation=evaluation, gamerecommended=GameRecommended.objects.get(recommendation=request.session['recommendation'], game=Game.objects.get(
                id_BGG=int(id_game))), interested=list_values["firstquestion"], buyorrecommend=list_values["secondquestion"], text=list_values["thirdquestion"], moreoptions=list_values["fourthquestion"])
            interaction.add_influences(list_values["fifthquestion"])

        if request.POST.get("button") == "exit":
            request.session.pop('recommendation', None)
            return redirect(reverse('list-questionnaries'))
        elif request.POST.get("button") == "moreEvals":
            request.session.pop('recommendation', None)
            # TODO: Guardar zacatrus_games?
            return render(request, 'newrecommendations.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL, 'preferences_part': answers})

    recommendation = Recommendation.objects.create(algorithm=Algorithm.objects.first(
    ), user=User.objects.get(id=request.session['userid']))
    recommendation.add_metrics(answers)

    request.session['recommendation'] = recommendation.id

    # TODO: Generar los juegos de recomendación desde las respuestas
    for game in zacatrus_games:
        GameRecommended.objects.create(recommendation=Recommendation.objects.get(id=request.session.get(
            'recommendation')), game=Game.objects.get_or_create(id_BGG=int(game[0]))[0])
    # TODO: Guardar datos del algoritmo

    return render(request, 'newrecommendations.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL, 'preferences_part': answers})


# TODO: quitar esto

def prueba(request):
    return render(request, 'prueba.html')
