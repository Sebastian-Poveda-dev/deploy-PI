from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0003_case_beneficiary'),
        ('users', '0002_create_default_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favorite_category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='preferred_by_users',
                to='cases.category',
            ),
        ),
    ]
