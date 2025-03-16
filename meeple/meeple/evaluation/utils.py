"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene métodos para la configuración del proyecto evaluation
"""
from django.shortcuts import resolve_url

def get_login_redirect_url(user):
    """Método para obtener la url a la que redirigirse en base al rol del usuario

    Args:
        user (User): objeto usuario que se encuentra autenticado

    Returns:
        str: Página a la que se redirige
    """
    if user.rol == 'CR':
        return resolve_url('my-studies')
    elif user.rol == 'PT':
        return resolve_url('list-questionnaires')
    return resolve_url('list-questionnaires')