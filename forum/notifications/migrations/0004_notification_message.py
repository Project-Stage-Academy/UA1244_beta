# Generated by Django 5.1.1 on 2024-11-07 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notification_expiration_notification_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
