import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
  help = "Generate a new module with the required structure."

  def add_arguments(self, parser):
    parser.add_argument('module_name', type=str, help="Name of the module to create")

  def handle(self, *args, **kwargs):
    module_name = kwargs['module_name']
    base_path = os.path.join('apps', module_name)  # Now pointing to the apps folder
        
    # Define file and directory structure
    structure = {
        'migrations': ['__init__.py'],
        '': ['__init__.py', 'apps.py', 'model.py', 'repository.py', 'serializer.py', 'service.py', 'urls.py', 'views.py']
    }

    module = module_name[0].upper() + module_name[1:-1]
        
    for folder, files in structure.items():
      folder_path = os.path.join(base_path, folder)
      os.makedirs(folder_path, exist_ok=True)
      for file in files:
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
          with open(file_path, 'w') as f:
          # Add default content based on file type
            if file == 'apps.py':
              f.write(f'from django.apps import AppConfig\n\nclass {module}Config(AppConfig):\n    name = "apps.{module_name}"\n')
            if file == 'urls.py':
              f.write('from django.urls import path\n\nurlPatterns = []\n')
            elif file == 'model.py':
              f.write(f'from apps.base.model import BaseModel\nfrom django.db import model\n\nclass {module}(BaseModel):\n    pass\n')
            elif file == 'repository.py':
              f.write(f'from apps.base.repository import BaseRepository\n'
                      f'from .model import {module}\n\n'
                      f'class {module}Repository(BaseRepository):\n'
                      f'  def __init__(self):\n'
                      f'    super().__init__({module})\n'
                    )
            elif file == 'serializer.py':
              f.write(f'from rest_framework import serializers\n\nclass {module}Serializer(serializers.ModelSerializer):\n    pass\n')
            elif file == 'service.py':
              module_lower = module.lower()
              f.write(f'from apps.base.service import BaseService\n'
                      f'from apps.{module_name}.repository import {module}Repository\n\n'
                      f'class {module}Service(BaseService):\n'
                      f'  def __init__(self, {module_lower}_repo: {module}Repository):\n'
                      f'    self.{module_lower}_repo = {module_lower}_repo\n'
                    )
            elif file == 'views.py':
              f.write('from rest_framework.decorators import api_view, permission_classes\n\n')
            else:
              f.write('\n')
      
      settings_path = os.path.join('bigapi', 'settings.py')
      with open(settings_path, 'r') as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
          if line.strip().startswith('INSTALLED_APPS'):
            break

        app_entry = f"    'apps.{module_name}',\n"
        if app_entry not in lines:
          for j in range(i, len(lines)):
              if lines[j].strip() == ']':
                lines.insert(j, app_entry)
                break

        with open(settings_path, 'w') as f:
          f.writelines(lines)
    self.stdout.write(self.style.SUCCESS(f"Module '{module_name}' created successfully!"))
