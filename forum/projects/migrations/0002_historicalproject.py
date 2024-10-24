# Generated by Django 5.1.1 on 2024-10-21 15:49

import django.db.models.deletion
import simple_history.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        ('startups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalProject',
            fields=[
                ('project_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('title', models.CharField(db_index=True, max_length=100)),
                ('description', models.TextField()),
                ('required_amount', models.DecimalField(decimal_places=2, max_digits=15)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('in progress', 'In Progress'), ('completed', 'Completed')], default='planned', max_length=20)),
                ('planned_start_date', models.DateField(blank=True, null=True)),
                ('actual_start_date', models.DateField(blank=True, null=True)),
                ('planned_finish_date', models.DateField(blank=True, null=True)),
                ('actual_finish_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('last_update', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('media', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='projects.media')),
                ('startup', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='startups.startup')),
            ],
            options={
                'verbose_name': 'historical Project',
                'verbose_name_plural': 'historical Projects',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
