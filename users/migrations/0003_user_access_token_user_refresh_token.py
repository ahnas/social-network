# Generated by Django 5.1.1 on 2024-09-26 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_rename_is_admin_user_is_staff_user_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='access_token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='refresh_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]
