from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Subclinic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class CaseStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'case statuses'


class Case(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_cases',
    )
    subclinic = models.ForeignKey(
        Subclinic,
        on_delete=models.PROTECT,
        related_name='cases',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='cases',
    )
    status = models.ForeignKey(
        CaseStatus,
        on_delete=models.PROTECT,
        related_name='cases',
    )
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='beneficiary_cases',
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CaseAssignment',
        related_name='assigned_cases',
    )

    def clean(self):
        super().clean()
        if self.beneficiary_id and not self.beneficiary.groups.filter(name='beneficiary').exists():
            raise ValidationError({'beneficiary': 'Selected user must belong to the beneficiary group.'})

    def __str__(self):
        return f'Case #{self.pk} — {self.status}'


class CaseAssignment(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='case_assignments',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('case', 'user')

    def __str__(self):
        return f'{self.user} → Case #{self.case_id}'


class CaseLog(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='case_logs',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Log by {self.user} on Case #{self.case_id}'
