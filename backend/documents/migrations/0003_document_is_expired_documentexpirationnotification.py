from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_alter_document_expiration_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='DocumentExpirationNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('upcoming', 'Upcoming'), ('expired', 'Expired')], max_length=20)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expiration_notifications', to='documents.document')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_expiration_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('document', 'recipient', 'event_type')},
            },
        ),
    ]
