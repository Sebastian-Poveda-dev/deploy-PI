from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_document_is_expired_documentexpirationnotification'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentexpirationnotification',
            name='priority',
            field=models.CharField(
                choices=[('medium', 'Medium'), ('high', 'High')],
                default='medium',
                max_length=20,
            ),
        ),
    ]
