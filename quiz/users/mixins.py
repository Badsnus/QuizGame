from django.contrib.auth.mixins import AccessMixin


class LogoutRequiredMixin(AccessMixin):
    """Verify that the current user is not authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
