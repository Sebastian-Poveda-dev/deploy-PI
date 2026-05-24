from django.contrib.auth.models import AbstractUser, Group
from django.db import models


DOCUMENT_TYPE_CHOICES = [
    ('CC', 'Cédula de ciudadanía'),
    ('CE', 'Cédula de extranjería'),
    ('TI', 'Tarjeta de identidad'),
    ('PA', 'Pasaporte'),
    ('NIT', 'NIT'),
    ('OTRO', 'Otro'),
]

MARITAL_STATUS_CHOICES = [
    ('SOLTERO', 'Soltero/a'),
    ('CASADO', 'Casado/a'),
    ('UNION_LIBRE', 'Unión libre'),
    ('DIVORCIADO', 'Divorciado/a'),
    ('VIUDO', 'Viudo/a'),
    ('SEPARADO', 'Separado/a'),
]

EDUCATION_LEVEL_CHOICES = [
    ('NINGUNO', 'Ninguno'),
    ('PRIMARIA', 'Primaria'),
    ('SECUNDARIA', 'Secundaria'),
    ('TECNICO', 'Técnico'),
    ('TECNOLOGO', 'Tecnólogo'),
    ('UNIVERSITARIO', 'Universitario'),
    ('POSGRADO', 'Posgrado'),
]

STRATUM_CHOICES = [(str(i), str(i)) for i in range(1, 7)]

RECEPTION_MEDIUM_CHOICES = [
    ('PRESENCIAL', 'Presencial'),
    ('TELEFONICA', 'Telefónica'),
    ('VIRTUAL', 'Virtual'),
    ('OTRO', 'Otro'),
]


class User(AbstractUser):
    identification_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES, blank=True)
    expedition_place = models.CharField(max_length=100, blank=True)
    landline_phone = models.CharField(max_length=20, blank=True)
    residence_address = models.CharField(max_length=255, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    stratum = models.CharField(max_length=1, choices=STRATUM_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    reception_medium = models.CharField(max_length=20, choices=RECEPTION_MEDIUM_CHOICES, blank=True)
    how_they_found_out = models.CharField(max_length=255, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    return_date = models.DateField(null=True, blank=True)
    extra_info = models.JSONField(default=dict, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        'cases.Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='advisors',
    )

    def assign_role(self, role_name):
        group = Group.objects.get(name=role_name)
        self.groups.clear()
        self.groups.add(group)

    def is_admin(self):
        return self.groups.filter(name='admin').exists()

    def is_advisor(self):
        return self.groups.filter(name='advisor').exists()

    def is_student(self):
        return self.groups.filter(name='student').exists()

    def is_beneficiary(self):
        return self.groups.filter(name='beneficiary').exists()
