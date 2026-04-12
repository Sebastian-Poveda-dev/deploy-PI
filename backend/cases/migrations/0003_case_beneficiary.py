from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_case_beneficiary(apps, schema_editor):
    Case = apps.get_model('cases', 'Case')
    User = apps.get_model('users', 'User')

    fallback_beneficiary = User.objects.filter(groups__name='beneficiary').order_by('id').first()

    for case in Case.objects.filter(beneficiary__isnull=True):
        case.beneficiary_id = (
            fallback_beneficiary.id if fallback_beneficiary is not None else case.created_by_id
        )
        case.save(update_fields=['beneficiary'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_create_default_groups'),
        ('cases', '0002_seed_lookup_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='beneficiary',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='beneficiary_cases',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_case_beneficiary, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='case',
            name='beneficiary',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='beneficiary_cases',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
