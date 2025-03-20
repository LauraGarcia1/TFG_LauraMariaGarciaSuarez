"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene métodos para la configuración del proyecto evaluation
"""
from django.apps import apps
from django.contrib.auth import get_user_model
from django.shortcuts import resolve_url

def get_login_redirect_url(user):
    """Método para obtener la url a la que redirigirse en base al rol del usuario

    Args:
        user (User): objeto usuario que se encuentra autenticado

    Returns:
        str: Página a la que se redirige
    """
    # Obtener el modelo User correctamente
    User = get_user_model()
    
    # Verificar si el usuario es una instancia de nuestro modelo personalizado
    if isinstance(user, User):
        if user.rol == "CR":  # Creator
            return resolve_url('my-studies')
        elif user.rol == "PT":  # Participant
            return resolve_url('my-recommendations')
    
    return resolve_url('home')
