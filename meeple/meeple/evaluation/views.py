from urllib import request
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate
from .forms import SignUpForm


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
                return redirect('user-home')

    return render(request, 'home.html')


def signup(request):
    """
        Función que muestra la página de registro

        Autor: Laura Mª García Suárez
    """

    if request.method == "POST":
        form = SignUpForm(request.POST)

        username = request.POST.get("username")
        password = request.POST.get("password")

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('user-home')
        else:
            print(form.errors)
    else:
        form = SignUpForm()

    return render(request, 'register.html', {'username': request.session['username'], 'password': request.session['password'], 'form': form})


def preferences(request):
    # TODO: obtener las preferencias y guardarlas en una BD
    if request.method == "POST":
        return redirect('user-home')
    return render(request, 'preferences.html')


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

    return render(request, 'recommendations.html')


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
    return render(request, 'newrecommendations.html')