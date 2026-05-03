from django import forms
from django.apps import apps
from django.conf import settings

from .models import Category, Subclinic

User = apps.get_model(settings.AUTH_USER_MODEL)


class CaseCreateForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=True,
    )
    subclinic = forms.ModelChoiceField(
        queryset=Subclinic.objects.all().order_by('name'),
        required=True,
    )
    beneficiary = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=True,
        empty_label='Select a beneficiary',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['beneficiary'].queryset = User.objects.filter(
            groups__name='beneficiary',
        ).order_by('first_name', 'last_name', 'username').distinct()
        self.fields['beneficiary'].label_from_instance = self._beneficiary_label

    @staticmethod
    def _beneficiary_label(user):
        full_name = f'{user.first_name} {user.last_name}'.strip()
        return full_name or user.username

class CaseCancellationRequestForm(forms.ModelForm):
    class Meta:
        from .models import CaseCancellationRequest
        model = CaseCancellationRequest
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the reason for reassignment (e.g., academic overload)'}),
        }


class CaseCancellationReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('approved', 'Approve'), ('rejected', 'Reject')],
        widget=forms.RadioSelect,
    )
