from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_user_beneficiary_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='extra_info',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
