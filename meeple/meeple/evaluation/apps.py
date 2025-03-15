"""
Author: Laura Mª García Suárez
Date: 2024-10-15
Description: Este archivo contiene la configuración del proyecto evaluation
"""
from django.apps import AppConfig

class EvaluationConfig(AppConfig):
    """Configuración de la aplicación 'evaluation'.

    Args:
        AppConfig (django.apps.AppConfig): Clase base para la configuración de aplicaciones en Django.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evaluation'
