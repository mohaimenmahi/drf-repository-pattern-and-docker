from django.db import migrations, models

def create_roles(apps, schema_editor):
  Role = apps.get_model('roles', 'Role')
  User = apps.get_model('users', 'User')

  admin_role, created = Role.objects.get_or_create(name='Admin')

  if created:
    print('Admin role created successfully.')
  else:
    print('Admin role already exists.')
    
  user_id = 1
  try:
    user = User.objects.get(id=user_id)
    user.roles.add(admin_role)
    user.save()
  except User.DoesNotExist:
    pass

class Migration(migrations.Migration):
  dependencies = [
    ('roles', '0001_initial'),
    ('users', '0006_user_roles')
  ]

  operations = [
    migrations.RunPython(create_roles),
  ]
