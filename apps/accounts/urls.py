"""
URL patterns for accounts app.
"""

from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('delete/', views.DeleteAccountView.as_view(), name='delete-account'),
    path('players/', views.PlayerListView.as_view(), name='player-list'),
    path('referees/', views.RefereeListView.as_view(), name='referee-list'),
    path('users/', views.UserListView.as_view(), name='user-list'),
]
