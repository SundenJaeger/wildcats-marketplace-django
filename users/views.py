from django.shortcuts import render
from django.views import View


# Create your views here.
class LoginPageView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)