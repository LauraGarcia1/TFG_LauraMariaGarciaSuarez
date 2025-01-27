from django.utils.translation import get_language
from django.conf import settings

def language_context(request):
    return {'LANGUAGE_CODE': get_language()}

def user_context(request):
    return {
        'user': request.user,
    }