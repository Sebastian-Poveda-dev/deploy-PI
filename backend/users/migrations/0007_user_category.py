import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0006_remove_professor_group'),
        ('cases', '0002_seed_lookup_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='advisors',
                to='cases.category',
            ),
        ),
    ]
