"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene los context processors personalizados del proyecto "evaluation". Estos context processors permiten añadir información adicional al contexto de las plantillas de Django.
"""
from django.utils.translation import get_language
from django.conf import settings

def language_context(request):
    """
    Añade el código del idioma actual al contexto global de las plantillas.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django.

    Returns:
        dict: Un diccionario con la clave 'LANGUAGE_CODE' y el valor del idioma actual.
    """
    return {'LANGUAGE_CODE': get_language()}

def user_context(request):
    """
    Añade la información del usuario autenticado al contexto global.

    Args:
        request (HttpRequest): Objeto de solicitud HTTP de Django.

    Returns:
        dict: Un diccionario con la clave 'user' y el valor del usuario actual.
    """
    return {
        'user': request.user,
    }