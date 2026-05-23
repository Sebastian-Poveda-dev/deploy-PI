from django.db import migrations


def remove_professor_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='professor').delete()


def restore_professor_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='professor')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_user_favorite_category'),
    ]

    operations = [
        migrations.RunPython(remove_professor_group, restore_professor_group),
    ]
