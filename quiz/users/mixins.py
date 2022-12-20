from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class LogoutRequiredMixin(AccessMixin):
    """Verify that the current user is not authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("users:profile")

        return super().dispatch(request, *args, **kwargs)
