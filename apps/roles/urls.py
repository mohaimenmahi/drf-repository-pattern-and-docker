from django.urls import path
from . import views

urlPatterns = [
  path('get-all-roles', views.get_all_roles),
  path('get-roles-by-admin', views.get_roles_by_admin),
  path('create-role', views.create_role),
  path('get-users-by-role/<int:role_id>', views.get_users_by_role),
]