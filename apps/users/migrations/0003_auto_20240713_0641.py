# Generated by Django 3.2.5 on 2024-07-13 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_users_phone_n_a3b1c5_idx'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='user',
            name='users_phone_n_a3b1c5_idx',
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['phone_number'], name='idx_phone_number'),
        ),
    ]