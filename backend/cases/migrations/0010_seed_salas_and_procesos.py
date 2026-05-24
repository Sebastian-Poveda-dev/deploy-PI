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


def seed_salas_and_procesos(apps, schema_editor):
    Category = apps.get_model('cases', 'Category')
    Subclinic = apps.get_model('cases', 'Subclinic')

    # Remove old lowercase duplicates that may exist from the initial seed
    Category.objects.filter(name__in=OLD_LOWERCASE).delete()

    for sala_name, procesos in SALAS_AND_PROCESOS.items():
        category, _ = Category.objects.get_or_create(name=sala_name)
        for proceso in procesos:
            Subclinic.objects.get_or_create(name=proceso, category=category)


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
