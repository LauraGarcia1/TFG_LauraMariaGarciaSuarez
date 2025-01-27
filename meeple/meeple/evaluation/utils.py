from django.shortcuts import resolve_url

def get_login_redirect_url(user):
    if user.rol == 'ER':
        return resolve_url('my-studies')
    elif user.rol == 'ED':
        return resolve_url('list-questionnaries')
    return resolve_url('list-questionnaries')