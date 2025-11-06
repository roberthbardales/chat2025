from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat_home, name='chat_home'),
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
]