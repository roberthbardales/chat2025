from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('chat/', views.ChatHomeView.as_view(), name='chat_home'),
    path('chat/<str:username>/', views.ChatRoomView.as_view(), name='chat_room'),
]