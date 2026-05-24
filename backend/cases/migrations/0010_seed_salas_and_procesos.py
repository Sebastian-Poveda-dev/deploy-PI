from django.db import migrations

SALAS_AND_PROCESOS = {
    'Civil': [
        'Proceso', 'Cobro pre-jurídico', 'Tutela', 'Derecho de petición',
        'Concepto + DP', 'Queja', 'Memorial', 'Concepto', 'Clínica empresarial',
    ],
    'Laboral': [
        'Proceso', 'Liquidación + concepto', 'Tutela', 'Derecho de petición',
        'Concepto', 'Queja', 'Memorial',
    ],
    'Penal': [
        'Proceso', 'Derecho de petición', 'Concepto + denuncia', 'Concepto', 'Memorial',
    ],
    'Familia': [
        'Proceso', 'Concepto + DP', 'Derecho de petición', 'Tutela',
        'Memorial', 'Queja', 'Cobro pre-jurídico', 'Concepto',
    ],
    'Derecho público': [
        'Proceso', 'Concepto + DP', 'Derecho de petición', 'Tutela',
        'Memorial', 'Queja', 'Cobro pre-jurídico', 'Concepto',
    ],
    'Derecho público - Migrantes': [
        'Solicitud de refugio', 'Solicitud de refugio + DP',
        'Solicitud de refugio + Tutela', 'Trámite salvoconducto',
        'Tutela', 'Concepto + DP', 'Derecho de petición', 'Concepto',
    ],
}

OLD_LOWERCASE = ['laboral', 'penal']

# Map from old lowercase name → new properly-cased name
RENAME_MAP = {
    'laboral': 'Laboral',
    'penal': 'Penal',
}


def seed_salas_and_procesos(apps, schema_editor):
    Category = apps.get_model('cases', 'Category')
    Subclinic = apps.get_model('cases', 'Subclinic')
    Case = apps.get_model('cases', 'Case')

    # Create all new categories first so we can reassign FKs before deleting old ones
    for sala_name, procesos in SALAS_AND_PROCESOS.items():
        category, _ = Category.objects.get_or_create(name=sala_name)
        for proceso in procesos:
            Subclinic.objects.get_or_create(name=proceso, category=category)

    # Reassign cases from old lowercase categories to new properly-cased ones
    for old_name, new_name in RENAME_MAP.items():
        old_cat = Category.objects.filter(name=old_name).first()
        if old_cat is None:
            continue
        new_cat = Category.objects.filter(name=new_name).first()
        if new_cat:
            Case.objects.filter(category=old_cat).update(category=new_cat)
        old_cat.delete()

    # Delete any remaining old lowercase categories that have no cases
    Category.objects.filter(name__in=OLD_LOWERCASE).delete()


def unseed_salas_and_procesos(apps, schema_editor):
    Category = apps.get_model('cases', 'Category')
    Category.objects.filter(name__in=SALAS_AND_PROCESOS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0009_case_immediate_resolution'),
    ]

    operations = [
        migrations.RunPython(seed_salas_and_procesos, unseed_salas_and_procesos),
    ]
