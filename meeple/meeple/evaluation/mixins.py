from django.http import HttpResponseForbidden

class RoleRequiredMixin:
    allowed_roles = []  # Lista vacía por defecto

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("No estás autenticado.")
        if request.user.rol not in self.allowed_roles:
            return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
        return super().dispatch(request, *args, **kwargs)