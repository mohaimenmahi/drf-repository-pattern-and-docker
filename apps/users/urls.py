from django.urls import path
from . import views

urlPatterns = [
  path('register', views.register),
  path('login', views.login),
  path('logout', views.logout),
  path('refresh-access-token', views.refresh_access_token),
  path('me', views.get_current_user),
  path('get-user/<int:id>', views.get_user),
  path('update-user-role', views.update_user_role),
]