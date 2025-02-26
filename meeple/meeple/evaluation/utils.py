from django.shortcuts import resolve_url

def get_login_redirect_url(user):
    if user.rol == 'CR':
        return resolve_url('my-studies')
    elif user.rol == 'PT':
        return resolve_url('list-questionnaires')
    return resolve_url('list-questionnaires')