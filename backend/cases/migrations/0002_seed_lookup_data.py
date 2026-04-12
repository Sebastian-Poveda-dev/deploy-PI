from django.db import migrations

DEFAULT_STATUSES = [
    'active',
    'pending_authorization',
    'in_progress',
    'finished',
    'inactive',
    'canceled',
]

DEFAULT_CATEGORIES = [
    'laboral',
    'penal',
]


def seed_data(apps, schema_editor):
    CaseStatus = apps.get_model('cases', 'CaseStatus')
    for name in DEFAULT_STATUSES:
        CaseStatus.objects.get_or_create(name=name)

    Category = apps.get_model('cases', 'Category')
    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name)


def unseed_data(apps, schema_editor):
    CaseStatus = apps.get_model('cases', 'CaseStatus')
    CaseStatus.objects.filter(name__in=DEFAULT_STATUSES).delete()

    Category = apps.get_model('cases', 'Category')
    Category.objects.filter(name__in=DEFAULT_CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, unseed_data),
    ]
