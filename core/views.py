from django.contrib.auth.views import LoginView
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    def get_success_url(self):
        if self.request.user.is_staff:
            return redirect('dashboard').url
        return redirect('portal_index').url
