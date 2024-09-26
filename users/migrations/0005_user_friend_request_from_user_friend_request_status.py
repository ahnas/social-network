# Generated by Django 5.1.1 on 2024-09-26 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_user_is_staff_alter_user_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='friend_request_from',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='friend_request_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
    ]
