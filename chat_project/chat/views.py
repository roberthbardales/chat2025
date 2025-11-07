from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView
from django.urls import reverse_lazy
from .models import Message


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'chat/register.html'
    success_url = reverse_lazy('chat_home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)
        return response


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'chat/login.html'
    success_url = reverse_lazy('chat_home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

    def post(self, request):
        logout(request)
        return redirect('login')


class ChatHomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'chat/home.html'
    context_object_name = 'users'
    login_url = '/login/'

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)


class ChatRoomView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/room.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        username = self.kwargs.get('username')
        other_user = User.objects.get(username=username)

        messages = Message.objects.filter(
            sender__in=[self.request.user, other_user],
            recipient__in=[self.request.user, other_user]
        ).order_by('timestamp')

        context['other_user'] = other_user
        context['messages'] = messages
        return context