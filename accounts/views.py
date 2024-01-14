from django.shortcuts import render,redirect
from django.views.generic import FormView
from .forms import UserRegform
from django.contrib.auth import login,logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from .forms import UserUpdateForm
from django.views import View
# Create your views here.
class UserRegView(FormView):
    template_name= 'accounts/user_reg.html'
    form_class = UserRegform
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name = 'accounts/user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')

def user_logout(req):
    logout(req)
    return redirect('login')

class UserBankAccountUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})

