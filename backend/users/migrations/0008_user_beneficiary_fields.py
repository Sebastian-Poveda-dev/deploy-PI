from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_user_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='document_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('CC', 'Cédula de ciudadanía'),
                    ('CE', 'Cédula de extranjería'),
                    ('TI', 'Tarjeta de identidad'),
                    ('PA', 'Pasaporte'),
                    ('NIT', 'NIT'),
                    ('OTRO', 'Otro'),
                ],
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='expedition_place',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='landline_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='user',
            name='neighborhood',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='department',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='stratum',
            field=models.CharField(
                blank=True,
                choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')],
                max_length=1,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='reception_medium',
            field=models.CharField(
                blank=True,
                choices=[
                    ('PRESENCIAL', 'Presencial'),
                    ('TELEFONICA', 'Telefónica'),
                    ('VIRTUAL', 'Virtual'),
                    ('OTRO', 'Otro'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='how_they_found_out',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='marital_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('SOLTERO', 'Soltero/a'),
                    ('CASADO', 'Casado/a'),
                    ('UNION_LIBRE', 'Unión libre'),
                    ('DIVORCIADO', 'Divorciado/a'),
                    ('VIUDO', 'Viudo/a'),
                    ('SEPARADO', 'Separado/a'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='education_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('NINGUNO', 'Ninguno'),
                    ('PRIMARIA', 'Primaria'),
                    ('SECUNDARIA', 'Secundaria'),
                    ('TECNICO', 'Técnico'),
                    ('TECNOLOGO', 'Tecnólogo'),
                    ('UNIVERSITARIO', 'Universitario'),
                    ('POSGRADO', 'Posgrado'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='occupation',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='return_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
