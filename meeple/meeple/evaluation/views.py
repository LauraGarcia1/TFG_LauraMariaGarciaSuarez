"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene funciones o clases del proyecto evaluation que controlan la lógica de negocio y gestionan las peticiones HTTP, manejan datos de los modelos, renderizan plantillas o devuelven respuestas JSON para la API
"""
import asyncio
from googletrans import Translator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connections
from django.views.generic.list import ListView
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from .decorators import role_required
from .mixins import RoleRequiredMixin
from .forms import QuestionForm, SectionForm, SignUpForm, QuestionnaireForm, SectionFormSet, QuestionFormSet, ChoiceForm, ChoiceFormSet
from .models import Preference, Creator, Participant, Game, Questionnaire, Question, Answer, Choice, Evaluation, Algorithm, Recommendation, Section
import json
import random
import re

def home(request):
    """Gestiona la página de inicio de Meeple

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con la página de registro o redirección.
    """
    title_home = _("Welcome")
    username_home = _("Username")
    password_home = _("Password")
    login_home = _("Login")
    signup_home = _("Sign up")

    if request.user.is_authenticated:
        if Creator.objects.filter(id=request.session.get('userid')).exists():
            return redirect(reverse('my-studies'))
        if Participant.objects.filter(id=request.session.get('userid')).exists():
            return redirect(reverse('my-recommendations'))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if request.POST.get("button") == "signin":
            user = authenticate(username=username, password=password)
            # Si existe el usuario
            if user is not None:
                login(request, user)
                request.session['userid'] = user.id
                # Comprobamos el tipo de usuario que es y redirigimos a la página correcta
                if Creator.objects.filter(id=user.id).exists():
                    return redirect(reverse('my-studies'))
                if Participant.objects.filter(id=user.id).exists():
                    return redirect(reverse('my-recommendations'))
            
            # Si el nombre de usuario existe, seguramente la contraseña es errónea
            if Creator.objects.filter(username=username).exists() or Participant.objects.filter(username=username).exists():
                message_error = _("WrongPassword")
                return render(request, 'home.html', {'title': title_home, 'username': username_home, 'password': password_home, 'login': login_home, 'signup': signup_home, 'redirect_to': request.path, 'message_error' : message_error})

        request.session['username'] = username
        request.session['password'] = password
        
        return redirect(reverse('register'))


    return render(request, 'home.html', {'title': title_home, 'username': username_home, 'password': password_home, 'login': login_home, 'signup': signup_home, 'redirect_to': request.path})


def signup(request):
    """Gestiona el registro de usuarios.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con la página de registro o redirección.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)

        username = request.POST.get("username")
        password = request.POST.get("password")
        rol = request.POST.get("rol")

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            request.session['userid'] = user.id

            if user is not None:
                login(request, user)
                # Comprobamos el tipo de usuario que es y redirigimos a la página correcta
                if rol == "CR":
                    return redirect('my-studies')
                if rol == "PT":
                    return redirect('preferences')
        else:
            print(form.errors)

    return render(request, 'register.html', {'username': request.session['username'], 'password': request.session['password']})

def logout(request):
    """Cierra la sesión del usuario.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponseRedirect: Redirige a la página de inicio.
    """
    request.session.flush()
    return redirect('home')
    

@login_required
@role_required(allowed_roles=['Participant', 'PT'])
def preferences(request):
    """Gestiona la vista de preferencias del usuario.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con la página de preferencias.
    """
    if request.method == "POST":
        preferences = request.POST.getlist('likedPreferences')

        for pref in preferences:
            with connections['external_db'].cursor() as cursor:
                cursor.execute(
                    "SELECT GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS categories FROM (SELECT DISTINCT gameid, name FROM zacatrus_game_categories) zgc WHERE zgc.gameid = %s;", [pref])
                categories = cursor.fetchone()

                cursor.execute(
                    "SELECT GROUP_CONCAT(DISTINCT zgc.name ORDER BY zgc.name ASC) AS contexts FROM (SELECT DISTINCT gameid, name FROM zacatrus_game_contexts) zgc WHERE zgc.gameid = %s;", [pref])
                contexts = cursor.fetchone()

            Preference.objects.create(game=Game.objects.get_or_create(id_BGG=int(pref))[0], category=str(
                categories), context=str(contexts), user=Participant.objects.get(id=request.session.get('userid')))

        if request.session.get('rol') == "CR":
            return redirect(reverse('my-studies'))
        return redirect(reverse('my-recommendations'))

    zacatrus_games = get_preferences_games()

    return render(request, 'preferences.html', {'zacatrus_games': zacatrus_games, 'MEDIA_URL': settings.MEDIA_URL})


def get_preferences_games():
    """Obtiene los juegos a mostrar en la página de preferencias.

    Returns:
        list: Lista de juegos
    """
    game_ids = [295947, 230802, 163412, 256952, 172931, 230914, 684487, 30933, 260605, 251219, 162886, 174430, 316554, 12333, 11825]
    ids_str = ', '.join(map(str, game_ids))

    # Construye la consulta con el filtro IN
    query = f"SELECT id, name FROM zacatrus_games WHERE id IN ({ids_str});"

    with connections['external_db'].cursor() as cursor:
        cursor.execute(query)
        zacatrus_games = cursor.fetchall()

        return zacatrus_games


def get_data_game(request):
    """Obtiene los datos de un juego específico.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        JsonResponse: Respuesta con los datos del juego en formato JSON.
    """
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
@role_required(allowed_roles=['Participant', 'PT'])
def questionnaires(request):
    """Función que muestra la página principal del usuario

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """

    if request.method == "POST":
        quest_id = request.POST.get("button")
        if quest_id:
            return redirect('questionnaire', quest_id)

        return redirect(reverse('home'))
    
    questionnaires = Questionnaire.objects.filter(uploaded=True)

    return render(request, 'liststudies.html', {'questionnaires' : questionnaires})

@login_required
@role_required(allowed_roles=['Creator', 'CR'])
def algorithms(request):
    """Función para mostrar los algoritmos existentes al usuario Creador.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """
    algorithms = [(asyncio.run(translate_text(algorithm.name, translation.get_language())), asyncio.run(translate_text(algorithm.description, translation.get_language()))) for algorithm in Algorithm.objects.all()]

    #for algorithm in Algorithm.objects.all():
    #    asyncio.run(translate_text(algorithm.name, translation.get_language()))

    return render(request, 'listalgorithms.html', {'algorithms' : algorithms})

class StudiesView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """Función para eliminar secciones de cuestionarios/estudios.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.
        pk (text): variable con la clave pública del objeto sección

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """
    model = Questionnaire
    template_name = 'mystudies.html'
    context_object_name = 'questionnaires'
    allowed_roles = ['Creator', 'CR']

    def get_queryset(self):
        return Questionnaire.objects.filter(user=self.request.user)

@login_required
@role_required(allowed_roles=['Creator', 'CR'])
def create_study(request):
    """Función para crear cuestionarios/estudios con sus respectivas secciones, preguntas y opciones.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """
    if request.method == 'POST':
        #print(request.POST)
        questionnaire_form = QuestionnaireForm(request.POST)

        if questionnaire_form.is_valid():
            questionnaire = questionnaire_form.save(commit=False)
            questionnaire.user = Creator.objects.filter(id=request.session.get('userid'))[0]
            questionnaire.save()
        
            number_sections = int(request.POST.get("sections-TOTAL_FORMS", "").strip() or 0)
            for section_index in range(0, number_sections+1):
                section_title_key = f"sections-{section_index}-title"
                section_title = request.POST.get(section_title_key, "").strip()
                section_algorithm_key = f"sections-{section_index}-algorithm"
                section_algorithm = request.POST.get(section_algorithm_key, "").strip()
                if section_title:
                    # Si hay secciones del cuestionario, las guardamos
                    if section_algorithm == '' or section_algorithm is None:
                        section = Section.objects.create(
                            questionnaire=questionnaire,
                            title=section_title,
                            algorithm=None
                        )
                    else:
                        section = Section.objects.create(
                            questionnaire=questionnaire,
                            title=section_title,
                            algorithm=Algorithm.objects.get(id=section_algorithm)
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
    
@login_required
@role_required(allowed_roles=['Creator', 'CR'])
def edit_study(request, pk):
    """Función para editar cuestionarios/estudios con sus respectivas secciones, preguntas y opciones.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """
    if request.method == 'POST':
        print(request.POST)
        questionnaire = Questionnaire.objects.get(id=pk)
        questionnaire.name = request.POST.get('name')
        questionnaire.description = request.POST.get('description')
        questionnaire.language = request.POST.get('language')

        questionnaire.save()

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
            section_algorithms = request.POST.getlist('algorithm')
            
            question_ids = request.POST.getlist('questions-id')
            question_texts = request.POST.getlist('question_text')
            question_types = request.POST.getlist('type')

            choice_ids = request.POST.getlist('choices-id')
            choice_texts = request.POST.getlist('choice_text')

            # ---- Actualizar secciones ---- > title
            sections_to_update = []
            sections_alg_to_update = []
            for section_id, title, algorithm in zip(section_ids, section_titles, section_algorithms):
                if algorithm == '':
                    section = Section(id=section_id, title=title)
                    sections_to_update.append(section)
                else:
                    section = Section(id=section_id, title=title, algorithm=Algorithm.objects.get(id=algorithm))
                    sections_alg_to_update.append(section)

            # Realizar la actualización en masa para las secciones
            if sections_to_update:
                Section.objects.bulk_update(sections_to_update, ['title'])
            if sections_alg_to_update:
                Section.objects.bulk_update(sections_alg_to_update, ['title', 'algorithm'])

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

            # Comprobamos si hay objetos nuevos dentro de las secciones existentes, si es así los creamos
            create_sections(request, questionnaire, question_ids, section_ids) # Comprobamos en secciones existentes

            create_sections(request, questionnaire, question_ids)

            # Redireccionar o mostrar mensaje de éxito
            return redirect('my-studies')
    
    # Si es GET, simplemente mostramos el formulario con los objetos existentes
    questionnaire = get_object_or_404(Questionnaire, id=pk, user=Creator.objects.get(id=request.session.get('userid')))
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
@role_required(allowed_roles=['Creator', 'CR'])
def delete_study(request, pk):
    """Función para eliminar cuestionarios/estudios.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django que contiene los datos enviados por el usuario.
        pk (text): variable con la clave pública del objeto cuestionario

    Returns:
        HttpResponse: Respuesta HTTP con una redirección o una plantilla renderizada.
    """

    # Obtenemos el cuestionario por su ID
    questionnaire = get_object_or_404(Questionnaire, pk=pk)

    # Eliminamos el cuestionario
    questionnaire.delete()
    return redirect('my-studies')  # Redirigimos a la lista de cuestionarios

@login_required
@role_required(allowed_roles=['Creator', 'CR'])
def upload_study(request, pk):
    """Función para subir los cuestionarios

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web.
        pk (text): variable con la clave pública del objeto cuestionario

    Returns:
        HttpResponseRedirect: redirección a la página de todos los estudios del usuario
    """
    questionnaire = get_object_or_404(Questionnaire, pk=pk)
    if not questionnaire.are_fields_filled():
        messages.error(request, _("UploadME1"))
        return redirect('my-studies')

    # Comprobamos que el cuestionario tenga una o varias secciones
    sections = questionnaire.sections.all()
    if not sections:
        # En caso de no existir, no se sube el cuestionario
        messages.error(request, _("UploadME2"))
        return redirect('my-studies')
    
    # Comprobamos que cada sección tenga una o varias preguntas
    for section in sections:
        if not section.are_fields_filled():
            messages.error(request, _("UploadME3"))
            return redirect('my-studies')
        
        questions = section.questions.all()
        if not questions:
            # En caso de no existir, no se sube el cuestionario
            messages.error(request, _("UploadME4"))
            return redirect('my-studies')
        
        # Comprobamos que cada pregunta específica tenga una o varias opciones
        for question in questions:
            if not question.are_fields_filled():
                messages.error(request, _("UploadME5"))
                return redirect('my-studies')
            if question.type == "SCRB" or question.type == "MCRB" or question.type == "SCCB" or question.type == "MCCB":
                # En el caso de deber tener, comprobamos
                choices = question.choices.all()
                if not choices:
                    # En caso de no existir, no se sube el cuestionario
                    messages.error(request, _("UploadME6"))
                    return redirect('my-studies')
                for choice in choices:
                    if not choice.are_fields_filled():
                        messages.error(request, _("UploadME7"))
                        return redirect('my-studies')

    # Dada una validación satisfactoria, subimos el cuestionario
    questionnaire.uploaded = True
    questionnaire.save()

    return redirect('my-studies')  # Redirige a la lista de cuestionarios

@login_required
@role_required(allowed_roles=['Creator', 'CR'])
def view_study(request, pk):
    """Función que muestra una visualización del cuesstionario al Creador

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web
        pk (text): variable con la clave pública del objeto cuestionario

    Returns:
        HttpResponse: renderización de la página de inicio del Participante
    """
    # Obtener el cuestionario
    questionnaire = get_object_or_404(Questionnaire, id=pk, user=Creator.objects.get(id=request.session.get('userid')))

    # Crear el diccionario de secciones y preguntas con sus elecciones
    sections_dict = {}
    for section in questionnaire.sections.all():
        questions_dict = {}

        for question in section.questions.all():
            # Formulario de pregunta y sus opciones de respuesta (si las tiene)
            choices = question.choices.all()

            choice_forms = [ChoiceForm(instance=choice) for choice in choices]
            for choice_form in choice_forms:
                for field in choice_form.fields.values():
                    field.widget.attrs['readonly'] = 'readonly'
                    field.widget.attrs['disabled'] = 'disabled'

            questions_dict[(question.question_text, question.type)] = choice_forms
        
        sections_dict[section.title] = questions_dict
    
    return render(request, 'viewstudy.html', {
        'questionnaire_name': questionnaire.name,
        'questionnaire_description': questionnaire.description,
        'sections_dict': sections_dict,
    })


@login_required
@role_required(allowed_roles=['Participant', 'PT'])
def homeParticipant(request):
    """Función que muestra la página principal del usuario Participante

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web

    Returns:
        HttpResponse: renderización de la página de inicio del Participante
    """

    if request.method == "POST":
        if request.POST.get("button") == "newrecommendation":
            return redirect(reverse('list-questionnaires'))

        return redirect(reverse('home'))

    evaluations_data = get_data_evaluations(request.user)

    # Uso de páginas para poder visualizar las evaluaciones mejor
    paginator = Paginator(evaluations_data, 5)

    # Obtener el número de página de la URL
    page_number = request.GET.get('page')
    #user_evaluations_page = paginator.get_page(page_number)
    try:
        # Obtener la página actual
        user_evaluations_page = paginator.page(page_number)
    except PageNotAnInteger:
        # Si el número de página no es un entero, mostrar la primera página
        user_evaluations_page = paginator.page(1)
    except EmptyPage:
        # Si el número de página está fuera de rango, mostrar la última página
        user_evaluations_page = paginator.page(paginator.num_pages)

    return render(request, 'myrecommendations.html', {'user_evaluations_page': user_evaluations_page, 'MEDIA_URL': settings.MEDIA_URL})

@login_required
@role_required(allowed_roles=['Participant', 'PT'])
def view_questionnaire(request, pk):
    """Función que muestra la página del cuestionario

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web
        pk (text): variable con la clave pública del objeto cuestionario

    Returns:
        HttpResponseRedirect: renderización de la página de visualización del cuestionario
    """

    user = Participant.objects.get(id=request.session.get('userid'))

    if request.method == "POST":
        try:
            selections = json.loads(request.POST.get('selections', '{}'))
        except json.JSONDecodeError:
            return redirect('list-questionnaires')
        questionnaire = Questionnaire.objects.get(id=pk)

        # Obtenemos todas las respuestas y las guardamos. Primero las respuestas a las 
        # preguntas con opciones, y luego las preguntas con respuesta de otro tipo.
        answers = {}
        for question_id, choice_ids in selections.items():
            # Guardamos las respuestas del participante
            question = Question.objects.get(id=question_id)
            for choice in choice_ids:
                answer = Answer.objects.create(question=question, choice=Choice.objects.get(id=choice), user=user, language=settings.LANGUAGE_CODE)
                if question.section.id not in answers:
                    answers[question.section.id] = []
                answers[question.section.id].append(answer.id)
        
        question_keys = [(key.split('-')[1], value) for key, value in request.POST.items() if key.startswith("choice-")]
        for key, answer_text in question_keys:
            question = Question.objects.get(id=int(key))
            if answer_text != "":
                answer = Answer.objects.create(question=question, text=answer_text, choice=None, user=user, language=settings.LANGUAGE_CODE)
                if question.section.id not in answers:
                    answers[question.section.id] = []
                answers[question.section.id].append(answer.id)
            

        # Creamos una evaluación por cada sección del cuestionario
        for section in questionnaire.sections.all():
            recommendation_game = request.POST.get(f"game-{section.id}")

            # Guardamos la recomendación dada al usuario
            recommendation = Recommendation.objects.create(game=Game.objects.get_or_create(id_BGG=int(recommendation_game))[0], algorithm=section.algorithm, metrics=get_responses_for_code(user=user))
            if section.id in answers:
                Evaluation.objects.create(recommendation=recommendation, user=user, answers=answers[section.id])

        redirection = request.POST.get("button")
        if redirection == "moreEvals":
            return redirect('list-questionnaires')
        
        return redirect('my-recommendations')
        
    # Obtener el cuestionario
    questionnaire = get_object_or_404(Questionnaire, id=pk)

    # Revisar que el cuestionario está subido/validado
    if questionnaire.uploaded:
        # Crear el diccionario de secciones y preguntas con sus elecciones
        responses = get_responses_for_code(user) # Obtenemos la información relevante de las preferencias del usuario
        sections_dict = {}
        for section in questionnaire.sections.all():
            # Obtener el juego del algoritmo
            game = execute_algorithm(code=section.algorithm.code, user=user, responses=responses)
            questions_dict = {}

            for question in section.questions.all():
                # Formulario de pregunta y sus opciones de respuesta (si las tiene)
                choices = question.choices.all()
                
                choice_forms = [ChoiceForm(instance=choice) for choice in choices]

                questions_dict[(question.question_text, question.type, question.id)] = choice_forms

            sections_dict[(section.title, section.id)] = {
                'questions': questions_dict,
                'game': game[0]
            }

        return render(request, 'viewquestionnaire.html', {
            'questionnaire_name': questionnaire.name,
            'questionnaire_description': questionnaire.description,
            'sections_dict': sections_dict,
            'MEDIA_URL': settings.MEDIA_URL
        })
    
    return redirect('list-questionnaires')



###### FUNCIONES GENERALES
def get_data_questions():
    """Función que obtiene las opciones de las preguntas

    Returns:
        dict: parámetros del usuario contenido en un diccionario
    """

    questionnaire = Questionnaire.objects.first()
    questions = questionnaire.questions.all()

    questions_and_choices = {
        question: question.choices.all() for question in questions
    }

    return questions_and_choices

async def translate_text(text, target_language):
    """Traduce un texto al idioma deseado usando Google Translate.

    Args:
        text (str): texto de entrada a traducir.
        target_language (str): código del idioma de destino.

    Returns:
        str: texto traducido.
    """
    # Crear un objeto de traductor
    translator = Translator()

    detected_language = await translator.detect(text)

    if detected_language.lang == target_language:
        return text
    
    # Traducir el texto al idioma deseado
    translated = await translator.translate(text, dest=target_language)
    
    return translated.text  # Devolver el texto traducido

def create_sections(request, questionnaire, question_ids, list_sections = None):
    """Función para crear las secciones desde las páginas de creación y edición de estudios

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web
        questionnaire (Questionnaire): cuestionario al que pertenecen las secciones
        question_ids (list): Lista de preguntas existentes 
        list_questions (List, optional): Lista de preguntas existentes. Defaults to None.
    """
    if list_sections is None:
        # Expresión regular para encontrar los preguntas que comienzan con "section-" y terminan con "-title"
        first_pattern = re.compile(r"^sections-(\d+)-title$")
        second_pattern = re.compile(r"^sections-(\d+)-algorithm$")

        # Filtrar las claves que coincidan con el patrón en request.POST
        matching_title = []
        matching_algorithm = []
        matching_section_indexes = []
        for key, value in request.POST.items():
            match_title = first_pattern.match(key)
            match_algorithm = second_pattern.match(key)

            if match_title:
                matching_title.append(value)
                matching_section_indexes.append(match_title.group(1))  # Extraer el índice (\d+)

            if match_algorithm:
                matching_algorithm.append(value)


        for title, algorithm, section_index in zip(matching_title, matching_algorithm, matching_section_indexes):
            # Crear la pregunta para la sección
            if algorithm == '':
                section = Section.objects.create(
                    questionnaire=questionnaire,
                    title=title
                )
            else:
                section = Section.objects.create(
                    questionnaire=questionnaire,
                    title=title,
                    algorithm=Algorithm.objects.get(id=algorithm)
                )

            # Procesar las preguntas de esta sección
            create_questions(request, section_index=section_index, language=questionnaire.language, assoc_section=section.id)

    else:
        for section in list_sections: # Comprobamos en secciones existentes
            create_questions(request, section_index=section, list_questions=question_ids, language=questionnaire.language)
            create_questions(request, section_index=section, language=questionnaire.language)

def create_questions(request, section_index, language, list_questions = None, assoc_section = None):
    """Función para crear las preguntas desde las páginas de creación y edición de estudios

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web
        section_index (text): Identificador de la Sección asociada a las preguntas
        language (text): Idioma del cuestionario
        list_questions (List, optional): Lista de preguntas existentes. Defaults to None.
    """
    if list_questions is None: # Creamos las preguntas nuevas
        # Expresión regular para encontrar los preguntas que comienzan con "questions-" y terminan con "{section_index}-question_text"
        first_pattern = re.compile(r"^questions-(\d+)-{}-question_text$".format(section_index))
        second_pattern = re.compile(r"^questions-(\d+)-{}-type$".format(section_index))

        # Filtrar las claves que coincidan con el patrón en request.POST
        matching_question_text = []
        matching_type = []
        matching_question_indexes = []
        for key, value in request.POST.items():
            match_text = first_pattern.match(key)
            match_type = second_pattern.match(key)

            if match_text:
                matching_question_text.append(value)
                matching_question_indexes.append(match_text.group(1))  # Extraer el índice (\d+)

            if match_type:
                matching_type.append(value)

        if assoc_section is None:
            section = Section.objects.get(id=int(section_index))
        else:
            section = Section.objects.get(id=int(assoc_section))

        for question_text, type, question_index in zip(matching_question_text, matching_type, matching_question_indexes):
            # Crear la pregunta para la sección
            question = Question.objects.create(
                section=section,
                question_text=question_text,
                type=type,
                language=language
            )

            create_choices(request, question.id, section_index = section_index, question_index = question_index) # Creamos las opciones nuevas 
    else:
        for question in list_questions: # Comprobamos en preguntas existentes
            create_choices(request, question, section_index = section_index, question_index = question) # Creamos las opciones nuevas


def create_choices(request, question, section_index, question_index):
    """Función para crear las opciones desde las páginas de creación y edición de estudios

    Args:
        request (HttpRequest): instancia de la clase HttpRequest fundamental para manejar las solicitudes HTTP en una aplicación web
        question (Question): Pregunta asociada a las opciones
        section_index (text): Identificador de la Sección asociada a las opciones
        question_index (text): Identificador de la Pregunta asociada a las opciones
    """
    # Expresión regular para encontrar los choices que comienzan con "choices-" y terminan con "{section_index}-{question_index}-choice_text"
    pattern = re.compile(r"^choices-(\d+)-{}-{}-choice_text$".format(section_index, question_index))

    # Filtrar las claves que coincidan con el patrón en request.POST
    matching_keys = [key for key in request.POST.keys() if pattern.match(key)]

    for choice in matching_keys:

        choice_keys = request.POST.get(choice, "").strip()
        if not choice_keys:
            # No se encontró más preguntas para esta sección
            break
        # Crear la pregunta para la sección
        Choice.objects.create(
            question=Question.objects.get(id=question),
            choice_text=choice_keys,
        )

def get_responses_for_code(user):
    """Función para obtener los datos del usuario que usaremos para los algoritmos de recomendación

    Args:
        user (User): Objeto tipo User que hace referencia al usuario actual

    Returns:
        dict: parámetros del usuario contenido en un diccionario
    """
    responses = {}
    # Obtener todas las categorías
    preferences = Preference.objects.filter(user=user)
    categories_tuples = preferences.values_list('category', flat=True)

    categories_list = []
    for cat in categories_tuples:
        cat = cat.strip("()").replace("'", "")
        categories_list.extend([category.strip() for category in cat.split(',')])

    responses['categories'] = list(set(cat for cat in categories_list if cat.strip()))

    # Obtener todas las contexts
    contexts_tuples = preferences.values_list('context', flat=True)

    contexts_list = []
    for ctx in contexts_tuples:
        ctx = ctx.strip("()").replace("'", "")
        contexts_list.extend([context.strip() for context in ctx.split(',')])

    responses['contexts'] = list(set(ctx for ctx in contexts_list if ctx.strip()))

    return responses

def get_data_evaluations(user):
    """Obtiene las evaluaciones del usuario con sus respuestas organizadas eficientemente.

    Args:
        user (User): El usuario autenticado

    Returns:
        list: Lista de evaluaciones con información estructurada.
    """

    # Obtenemos todas las evaluaciones del usuario con la recomendación y el juego asociado.
    evaluations = Evaluation.objects.filter(user=user).select_related('recommendation__game').order_by('-date_created')
    
    evaluations_data = []
    
    for evaluation in evaluations:
        answers_json = evaluation.answers
        if not answers_json:
            continue
        
        # Extraemos todos los IDs de preguntas presentes en la evaluación
        question_answers = {}
        question_info = {}
        for ans in answers_json:
            answer = Answer.objects.get(id=ans)

            if answer.question.id not in question_answers:
                question_answers[answer.question.id] = []
            if answer.question.id not in question_info:
                question_info[answer.question.id] = answer.question.question_text

            question_answers[answer.question.id].append(answer.text if answer.text is not None else answer.choice.choice_text)
        
        if not question_answers:
            continue

        # Obtenemos el título del cuestionario y de la sección
        first_qid = next(iter(question_answers))
        first_question = Question.objects.get(id=first_qid)
        section = first_question.section if first_question else None
        questionnaire = section.questionnaire if section else None

        formatted_data = {question_info[q_id]: answers for q_id, answers in question_answers.items()}

        evaluations_data.append({
            'questionnaire_title': questionnaire.name if questionnaire else "Unknown",
            'section_title': section.title if section else "Unknown",
            'date_created': evaluation.date_created,
            'game_id': evaluation.recommendation.game.id_BGG if evaluation.recommendation and evaluation.recommendation.game else None,
            'questions': formatted_data
        })

    return evaluations_data


def execute_algorithm(code, user, responses, number_sections = 1):
    """Función para ejecutar los algoritmos de recomendación guardados en la base de datos del proyecto

    Args:
        code (text): Parámetro con el código en forma de texto
        user (User): El usuario autenticado
        responses (List, optional): Las categorías encontradas en las preferencias del usuario. Defaults to None.

    Returns:
        list: Listado de juegos recomendados
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
            return environment["recommend"](user, responses, number_sections)
        else:
            return ["Error: The algorithm must define the function 'recommend(user, responses)'."]
    except Exception as e:
        return [f"Algorithm execution error: {str(e)}"]