from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_identification_number'),
        ('cases', '0002_seed_lookup_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='favorite_category',
        ),
    ]
