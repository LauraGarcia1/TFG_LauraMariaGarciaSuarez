import asyncio
from googletrans import Translator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.db import connections
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from .forms import QuestionForm, SectionForm, SignUpForm, QuestionnaireForm, SectionFormSet, QuestionFormSet, ChoiceForm, ChoiceFormSet
from .models import Preference, User, Game, Questionnaire, Question, Answer, Choice, Evaluation, Algorithm, Recommendation,  GameRecommended, Interaction, Section
import json
import random

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
        if User.objects.get(id=request.session.get('userid')).rol == "CR":
            return redirect(reverse('my-studies'))
        
        return redirect(reverse('my-recommendations'))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if request.POST.get("button") == "signin":
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['userid'] = user.id
                if user.rol == "CR":
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
                if user.rol == "PT":
                    return redirect('preferences')
                return redirect('my-studies')
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
    # TODO: solo podrá entrar en caso de que sea su primera vez escogiendo
    if request.method == "POST":
        preferences = request.POST.getlist('likedPreferences')

        for pref in preferences:
            with connections['external_db'].cursor() as cursor:
                cursor.execute(
                    "SELECT GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories FROM (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc WHERE zgc.gameid = %s;", [pref])
                categories = cursor.fetchone()

            Preference.objects.create(text=Game.objects.get_or_create(id_BGG=int(pref))[0], category=str(
                categories), value=0, user=User.objects.get(id=request.session.get('userid')))

        if request.session.get('rol') == "CR":
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

            # Al enviar los resultados, enviamos el contenido en el idioma usado por el usuario
            name = asyncio.run(translate_text(result[0], translation.get_language()))
            description = asyncio.run(translate_text(result[1], translation.get_language()))
            categories = asyncio.run(translate_text(result[2], translation.get_language()))
            ratings = asyncio.run(translate_text(result[3], translation.get_language()))
            types = asyncio.run(translate_text(result[4], translation.get_language()))
            contexts = asyncio.run(translate_text(result[5], translation.get_language()))
            
            if result:
                return JsonResponse({'name': name, 'description': description, 'categories': categories, 'ratings': ratings, 'types': types, 'contexts': contexts})
            else:
                return JsonResponse({'error': 'No se encontraron datos'})

@login_required
def questionnaires(request):
    """
        Función que muestra la página principal del usuario

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        quest_id = request.POST.get("button")
        if quest_id:
            return redirect('questionnaire', quest_id)

        return redirect(reverse('home'))
    
    questionnaires = Questionnaire.objects.filter(uploaded=True)

    return render(request, 'liststudies.html', {'questionnaires' : questionnaires})

class StudiesView(LoginRequiredMixin, ListView):
    """
        Función que muestra la página principal del usuario con rol Evaluador.

        Autor: Laura Mª García Suárez
    """
    model = Questionnaire
    template_name = 'mystudies.html'
    context_object_name = 'questionnaires'

    def get_queryset(self):
        return Questionnaire.objects.filter(user=self.request.user)
    
def delete_section(request, pk):
    try:
        section = Section.objects.get(id=pk)
    except Section.DoesNotExist:
        messages.success(
            request, 'Object Does not exist'
        )
        return redirect('edit-questionnaire', pk=section.questionnaire.id)

@login_required
def create_study(request):
    """Función para crear cuestionarios/estudios con sus respectivas secciones, preguntas y opciones.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """
    if request.method == 'POST':
        print(request.POST)
        questionnaire_form = QuestionnaireForm(request.POST)

        if questionnaire_form.is_valid():
            questionnaire = questionnaire_form.save(commit=False)
            questionnaire.user = User.objects.get(id=request.session.get('userid'))
            questionnaire.save()
        
            number_sections = int(request.POST.get("sections-TOTAL_FORMS", "").strip() or 0)
            for section_index in range(0, number_sections+1):
                section_title_key = f"sections-{section_index}-title"
                section_title = request.POST.get(section_title_key, "").strip()
                if section_title:
                    # Si hay secciones del cuestionario, las guardamos
                    section = Section.objects.create(
                        questionnaire=questionnaire,
                        title=section_title
                    )
                    # Procesar las preguntas de esta sección
                    number_questions = int(request.POST.get(f"questions-{section_index}-TOTAL_FORMS", "").strip() or 0)
                    for question_index in range(0, number_questions+1):
                        question_key_prefix = f"questions-{question_index}-{section_index}"
                        question_keys = [value for key, value in request.POST.items() if key.startswith(question_key_prefix)]
                        if question_keys:
                            # Si hay preguntas de la sección, las guardamos
                            question = Question.objects.create(
                                section=section,
                                question_text=question_keys[0],
                                type=question_keys[1],
                                language=questionnaire.language
                            )
                            number_choices = int(request.POST.get(f"choices-{section_index}-{question_index}-TOTAL_FORMS", "").strip() or 0)
                            for choice_index in range(0, number_choices):
                                choice_keys = request.POST.get(f"choices-{choice_index}-{section_index}-{question_index}-choice_text", "").strip()
                                if choice_keys:
                                    # Si hay opciones de la pregunta, las guardamos
                                    Choice.objects.create(
                                        question=question,
                                        choice_text=choice_keys,
                                    )

            # Redireccionar o mostrar mensaje de éxito
            return redirect('my-studies')
    
    # Si es GET, simplemente mostramos el formulario vacío
    questionnaire_form = QuestionnaireForm()
    section_formset = SectionFormSet(queryset=Section.objects.none(), prefix='sections')
    question_formset = QuestionFormSet(prefix='questions')
    choice_formset = ChoiceFormSet(queryset=Choice.objects.none(), prefix='choices')

    return render(request, 'createstudy.html', {
        'questionnaire_form': questionnaire_form,
        'section_formset': section_formset,
        'question_formset': question_formset,
        'choice_formset': choice_formset,
    })

def create_section_ajax(request):
    if request.method == "POST":
        title = request.POST.get("title", "")
        section = Section.objects.create(title=title)
        return JsonResponse({"id": section.id})
    
@login_required
def edit_study(request, pk):
    """Función para editar cuestionarios/estudios con sus respectivas secciones, preguntas y opciones.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """
    if request.method == 'POST':
        print(request.POST, pk)
        questionnaire = Questionnaire.objects.get(id=pk)
        questionnaire.name = request.POST.get('name')
        questionnaire.description = request.POST.get('description')
        questionnaire.language = request.POST.get('language')

        if questionnaire:
            # Comprobamos si hay objetos a eliminar y de ser así se eliminan
            delete_sections_list = request.POST.getlist('deleted_section_ids')[0]
            delete_questions_list = request.POST.getlist('deleted_question_ids')[0]
            delete_choices_list = request.POST.getlist('deleted_choice_ids')[0]

            
            if delete_sections_list:
                delete_sections_list = [int(section_id) for section_id in delete_sections_list.split(',') if section_id]
                sections_to_delete = Section.objects.filter(id__in=delete_sections_list)
                sections_to_delete.delete()

            if delete_questions_list:
                delete_questions_list = [int(question_id) for question_id in delete_questions_list.split(',') if question_id]
                questions_to_delete = Question.objects.filter(id__in=delete_questions_list)
                questions_to_delete.delete()

            if delete_choices_list:
                delete_choices_list = [int(choice_id) for choice_id in delete_choices_list.split(',') if choice_id]
                choices_to_delete = Choice.objects.filter(id__in=delete_choices_list)
                choices_to_delete.delete()

            # Comprobamos si hay que actualizar algún objeto
            section_ids = request.POST.getlist('sections-id')
            section_titles = request.POST.getlist('title')
            
            question_ids = request.POST.getlist('questions-id')
            # TODO: este campo hay que solucionarlo
            question_texts = request.POST.getlist('question_text')
            question_types = request.POST.getlist('question_type')

            choice_ids = request.POST.getlist('choices-id')
            choice_texts = request.POST.getlist('choice_text')

            # ---- Actualizar secciones ---- > title
            sections_to_update = []
            for section_id, title in zip(section_ids, section_titles):
                section = Section(id=section_id, title=title)
                sections_to_update.append(section)

            # Realizar la actualización en masa para las secciones
            if sections_to_update:
                Section.objects.bulk_update(sections_to_update, ['title'])

            # ---- Actualizar preguntas ---- > question_text, type, language
            questions_to_update = []
            for question_id, text, type in zip(question_ids, question_texts, question_types):
                question = Question(id=question_id, question_text=text, type=type, language=questionnaire.language)
                questions_to_update.append(question)

            # Realizar la actualización en masa para las preguntas
            if questions_to_update:
                Question.objects.bulk_update(questions_to_update, ['question_text', 'type', 'language'])

            # ---- Actualizar opciones ---- > choice_text
            choices_to_update = []
            for choice_id, text in zip(choice_ids, choice_texts):
                choice = Choice(id=choice_id, choice_text=text)
                choices_to_update.append(choice)

            # Realizar la actualización en masa para las opciones
            if choices_to_update:
                Choice.objects.bulk_update(choices_to_update, ['choice_text'])

            # Comprobamos si hay objetos nuevos, si es así los creamos
            for section in section_ids: # Comprobamos en secciones existentes
                create_questions(request, section_index=section, list_questions=question_ids)
                create_questions(request, section_index=section)

            section_index = 0
            while True: # Creamos las secciones nuevas y comprobamos su contenido
                section_title_key = f"sections-{section_index}-title"
                section_title = request.POST.get(section_title_key, "").strip()
                if not section_title:
                    # Si no se encuentra un título, asumimos que ya no hay más secciones
                    break

                section = Section.objects.create(
                    questionnaire=questionnaire,
                    title=section_title
                )
                # Procesar las preguntas de esta sección
                create_questions(request, section_index=section, list_questions=question_ids)
                create_questions(request, section_index=section)

                # Incrementamos el índice de sección y seguimos con la siguiente
                section_index += 1

            # Redireccionar o mostrar mensaje de éxito
            return redirect('my-studies')
    
    # Si es GET, simplemente mostramos el formulario con los objetos existentes
    questionnaire = get_object_or_404(Questionnaire, id=pk, user=User.objects.get(id=request.session.get('userid')))
    sections_dict = {}
    for section in questionnaire.sections.all():
        question_forms = {}

        for question in section.questions.all():

            choices = question.choices.all()

            question_forms[QuestionForm(instance=question)] = [ChoiceForm(instance=choice) for choice in choices]
            
        sections_dict[SectionForm(instance=section)] = question_forms
    
    questionnaire_form = QuestionnaireForm(instance=questionnaire)

    # Y enviamos el formulario vacío por si se creasen nuevos objetos
    section_formset = SectionFormSet(queryset=Section.objects.none(), prefix='sections')
    question_formset = QuestionFormSet(prefix='questions')
    choice_formset = ChoiceFormSet(queryset=Choice.objects.none(), prefix='choices')

    return render(request, 'editstudy.html', {
        'questionnaire': questionnaire_form, 
        'sections_dict': sections_dict,
        'section_formset': section_formset,
        'question_formset': question_formset,
        'choice_formset': choice_formset
        })

@login_required
def delete_study(request, pk):
    # Obtenemos el cuestionario por su ID
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    # Eliminamos el cuestionario
    questionnaire.delete()
    return redirect('my-studies')  # Redirigimos a la lista de cuestionarios

@login_required
def upload_study(request, pk):
    # Obtén el cuestionario por su ID
    questionnaire = get_object_or_404(Questionnaire, pk=pk)
    questionnaire.uploaded = True
    questionnaire.save()

    return redirect('my-studies')  # Redirige a la lista de cuestionarios

@login_required
def view_study(request, pk):
    # Obtener el cuestionario
    questionnaire = get_object_or_404(Questionnaire, id=pk, user=User.objects.get(id=request.session.get('userid')))
    
    # Crear el formulario del cuestionario y deshabilitar los campos
    questionnaire_form = QuestionnaireForm(instance=questionnaire)
    for field in questionnaire_form.fields.values():
        field.widget.attrs['readonly'] = 'readonly'
        field.widget.attrs['disabled'] = 'disabled'

    # Crear el diccionario de secciones y preguntas con sus elecciones
    sections_dict = {}
    for section in questionnaire.sections.all():
        question_forms = {}

        for question in section.questions.all():
            # Formulario de pregunta y sus opciones de respuesta (si las tiene)
            choices = question.choices.all()
            question_form = QuestionForm(instance=question)
            
            # Deshabilitar todos los campos de la pregunta
            for field in question_form.fields.values():
                field.widget.attrs['readonly'] = 'readonly'
                field.widget.attrs['disabled'] = 'disabled'

            choice_forms = [ChoiceForm(instance=choice) for choice in choices]
            for choice_form in choice_forms:
                for field in choice_form.fields.values():
                    field.widget.attrs['readonly'] = 'readonly'
                    field.widget.attrs['disabled'] = 'disabled'

            question_forms[question_form] = choice_forms
        
        section_form = SectionForm(instance=section)
        for field in section_form.fields.values():
            field.widget.attrs['readonly'] = 'readonly'
            field.widget.attrs['disabled'] = 'disabled'

        sections_dict[section_form] = question_forms
    
    return render(request, 'viewstudy.html', {
        'questionnaire_form': questionnaire_form,
        'sections_dict': sections_dict,
    })


@login_required
def recommendPage(request):
    """
        Función que muestra la página de recomendaciones

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        if request.POST.get("button") == "newrecommendation":
            return redirect(reverse('list-questionnaires'))
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
def view_questionnaire(request, pk):
    """
        Función que muestra la página del cuestionario

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        print(request.POST, "el cuestionario tiene pk", pk)
        selections = json.loads(request.POST.get('selections', '{}'))
        questionnaire = Questionnaire.objects.get(id=pk)
        # TODO: validación
        evaluation = Evaluation()

        answers = []
        for question_id, choice_ids in selections.items():
            # Guardamos las respuestas del participante
            # TODO: language no es correcto
            question = Question.objects.get(id=question_id)
            for choice in choice_ids:
                answer = Answer.objects.create(question=question, choice=Choice.objects.get(id=choice), user=User.objects.get(id=request.session.get('userid')), language=settings.LANGUAGE_CODE)
                answers.append(answer.choice)

        return redirect('newrecomm')
        
    # Obtener el cuestionario
    questionnaire = get_object_or_404(Questionnaire, id=pk)

    # Revisar que el cuestionario está subido/validado
    if questionnaire.uploaded:
        # Crear el formulario del cuestionario y deshabilitar los campos
        questionnaire_form = QuestionnaireForm(instance=questionnaire)
        for field in questionnaire_form.fields.values():
            field.widget.attrs['readonly'] = 'readonly'
            field.widget.attrs['disabled'] = 'disabled'

        # Crear el diccionario de secciones y preguntas con sus elecciones
        sections_dict = {}
        for section in questionnaire.sections.all():
            question_forms = {}

            for question in section.questions.all():
                # Formulario de pregunta y sus opciones de respuesta (si las tiene)
                choices = question.choices.all()
                question_form = QuestionForm(instance=question)
                
                # Deshabilitar todos los campos de la pregunta
                for field in question_form.fields.values():
                    field.widget.attrs['readonly'] = 'readonly'
                    field.widget.attrs['disabled'] = 'disabled'
                
                choice_forms = [ChoiceForm(instance=choice) for choice in choices]

                question_forms[question_form] = choice_forms
            
            section_form = SectionForm(instance=section)
            for field in section_form.fields.values():
                field.widget.attrs['readonly'] = 'readonly'
                field.widget.attrs['disabled'] = 'disabled'

            # Obtener todas las categorías
            categories_tuples = Preference.objects.values_list('category', flat=True)

            categories_list = []
            for cat in categories_tuples:
                cat = cat.strip("()").replace("'", "")
                categories_list.extend([category.strip() for category in cat.split(',')])

            unique_categories = list(set(cat for cat in categories_list if cat.strip()))

            # Obtener el juego del algoritmo
            assigned_game = execute_algorithm(code=section.algorithm.code, user=User.objects.get(id=request.session.get('userid')), responses=unique_categories)

            sections_dict[section_form] = {
                'questions': question_forms,
                'game': assigned_game
            }

        return render(request, 'viewquestionnaire.html', {
            'questionnaire_form': questionnaire_form,
            'sections_dict': sections_dict,
            'MEDIA_URL': settings.MEDIA_URL
        })
    
    return render(request, 'viewquestionnaire.html', {
        'questionnaire_form': None,
        'sections_dict': None,
    })


def get_data_questions():
    """
        Función que obtiene las opciones de las preguntas

        Autor: Laura Mª García Suárez
    """

    # TODO: como hago con los cuestionarios
    questionnaire = Questionnaire.objects.first()
    questions = questionnaire.questions.all()

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

        for id_game, list_values in selections.items():
            interaction = Interaction.objects.create(evaluation=evaluation, gamerecommended=GameRecommended.objects.get(recommendation=request.session['recommendation'], game=Game.objects.get(
                id_BGG=int(id_game))), interested=list_values["firstquestion"], buyorrecommend=list_values["secondquestion"], text=list_values["thirdquestion"], moreoptions=list_values["fourthquestion"])
            interaction.add_influences(list_values["fifthquestion"])

        if request.POST.get("button") == "exit":
            request.session.pop('recommendation', None)
            return redirect(reverse('list-questionnaires'))
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

###### FUNCIONES GENERALES

async def translate_text(text, target_language):
    # Crear un objeto de traductor
    translator = Translator()

    detected_language = await translator.detect(text)

    if detected_language.lang == target_language:
        return text
    
    # Traducir el texto al idioma deseado
    translated = await translator.translate(text, dest=target_language)
    
    return translated.text  # Devolver el texto traducido

def create_questions(request, section_index, list_questions = None):
    if list_questions is None:
        question_index = 0
        while True: # Creamos las preguntas nuevas y comprobamos su contenido
            question_key_prefix = f"questions-{section_index}-{question_index}"
            question_keys = [value for key, value in request.POST.items() if key.startswith(question_key_prefix)]
            if not question_keys:
                # No se encontró más preguntas para esta sección
                break
            # Crear la pregunta para la sección
            question = Question.objects.create(
                section=Section.objects.get(id=section_index),
                question_text=question_keys[0],
                type=question_keys[1],
                language=question_keys[2]
            )

            create_choices(request, question, section_index = section_index, question_index = question_index) # Creamos las opciones nuevas
            question_index += 1
    else:
        for question in list_questions: # Comprobamos en preguntas existentes
            create_choices(request, question, section_index = section_index, question_index = question) # Creamos las opciones nuevas


def create_choices(request, question, section_index, question_index):
    """Función para crear las opciones desde las páginas de creación y edición de estudios

    Args:
        request (HttpRequest):  instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web.
        question (Question): Pregunta asociada a las opciones
        section_index (text): Identificador de la Sección asociada a las opciones
        question_index (text): Identificador de la Pregunta asociada a las opciones
    """
    choice_index = 0
    while True:
        choice_text_key = f"choices-{choice_index}-{section_index}-{question_index}-choice_text"
        choice_keys = request.POST.get(choice_text_key, "").strip()
        if not choice_keys:
            # No se encontró más preguntas para esta sección
            break
        # Crear la pregunta para la sección
        Choice.objects.create(
            question=Question.objects.get(id=question),
            choice_text=choice_keys,
        )
        choice_index += 1

def execute_algorithm(code, user, responses = None):
    """Función para ejecutar los algoritmos de recomendación guardados en la base de datos del proyecto

    Args:
        code (text): Parámetro con el código en forma de texto
        user (User): El usuario autenticado
        responses (List, optional): Las categorías encontradas en las preferencias del usuario. Defaults to None.

    Returns:
        _type_: Juego recomendado
    """
    environment = {}

    def db_query(sql, params=None):
        """
        Ejecuta una consulta SQL en la base de datos 'external_db' y retorna los resultados.
        """
        with connections['external_db'].cursor() as cursor:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
    
    # Definir un entorno restringido para evitar ejecuciones peligrosas
    safe_builtins = {
        "print": print,
        "list": list,
        "dict": dict,
        "int": int,
        "float": float,
        "str": str,
        "len": len,
        "range": range,
        "db_query": db_query # Para acceder a la BD desde el algoritmo
    }

    try:
        # Ejecutar el código del usuario en un espacio controlado
        exec(code, {"__builtins__": safe_builtins, "random": random}, environment)
        
        # Verificar que el código haya definido la función necesaria
        if "recommend" in environment:
            return environment["recommend"](user, responses)
        else:
            return ["Error: The algorithm must define the function 'recommend(user, responses)'."]
    except Exception as e:
        return [f"Algorithm execution error: {str(e)}"]

# TODO: quitar esto

def prueba(request):
    return render(request, 'prueba.html')
