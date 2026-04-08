from django.db import migrations

DEFAULT_GROUPS = ['admin', 'advisor', 'professor', 'student', 'beneficiary']


def create_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in DEFAULT_GROUPS:
        Group.objects.get_or_create(name=name)


def delete_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=DEFAULT_GROUPS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_groups, delete_default_groups),
    ]
