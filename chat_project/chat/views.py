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

from django.http import JsonResponse

class ChatHomeView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'chat/home.html'
    context_object_name = 'users'
    login_url = '/login/'

    def get_queryset(self):
        users = User.objects.exclude(id=self.request.user.id)
        from .models import UserStatus
        status_map = {s.user_id: s.is_online for s in UserStatus.objects.all()}
        for user in users:
            user.is_online = status_map.get(user.id, False)
        return users

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('json') == '1':
            data = {user.id: user.is_online for user in context['users']}
            return JsonResponse(data)
        return super().render_to_response(context, **response_kwargs)



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from .models import Message

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

        # Formateamos la hora de cada mensaje
        messages_with_time = []
        for msg in messages:
            messages_with_time.append({
                'sender': msg.sender,
                'content': msg.content,
                'formatted_time': msg.timestamp.strftime('%H:%M')
            })

        context['other_user'] = other_user
        context['messages'] = messages_with_time
        return context


from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserStatus
from django.utils import timezone

@receiver(user_logged_in)
def set_user_online(sender, user, request, **kwargs):
    status, created = UserStatus.objects.get_or_create(user=user)
    status.is_online = True
    status.last_seen = timezone.now()
    status.save()

@receiver(user_logged_out)
def set_user_offline(sender, user, request, **kwargs):
    try:
        status = UserStatus.objects.get(user=user)
        status.is_online = False
        status.last_seen = timezone.now()
        status.save()
    except UserStatus.DoesNotExist:
        pass
