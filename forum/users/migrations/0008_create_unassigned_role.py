from django.db import migrations

def create_unassigned_role(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    Role.objects.get_or_create(name='unassigned')

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_user_options_user_active_role_alter_role_name'),  
    ]

    operations = [
        migrations.RunPython(create_unassigned_role),
    ]