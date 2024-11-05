# Generated by Django 5.1.1 on 2024-10-13 11:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_is_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AddField(
            model_name='user',
            name='active_role',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_users', to='users.role'),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(choices=[('startup', 'Startup'), ('investor', 'Investor'), ('unassigned', 'Unassigned')], max_length=50),
        ),
    ]