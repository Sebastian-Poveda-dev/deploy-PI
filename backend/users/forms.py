from django import forms
from django.contrib.auth import get_user_model

from .models import DOCUMENT_TYPE_CHOICES, MARITAL_STATUS_CHOICES, EDUCATION_LEVEL_CHOICES, STRATUM_CHOICES, RECEPTION_MEDIUM_CHOICES

User = get_user_model()


class BeneficiaryRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    identification_number = forms.CharField(max_length=30, required=True)
    document_type = forms.ChoiceField(choices=[('', '---------')] + list(DOCUMENT_TYPE_CHOICES), required=False)
    expedition_place = forms.CharField(max_length=100, required=False)
    landline_phone = forms.CharField(max_length=20, required=False)
    residence_address = forms.CharField(max_length=255, required=True)
    neighborhood = forms.CharField(max_length=100, required=False)
    city = forms.CharField(max_length=100, required=False)
    department = forms.CharField(max_length=100, required=False)
    stratum = forms.ChoiceField(choices=[('', '---------')] + list(STRATUM_CHOICES), required=False)
    phone_number = forms.CharField(max_length=20, required=True)
    reception_medium = forms.ChoiceField(choices=[('', '---------')] + list(RECEPTION_MEDIUM_CHOICES), required=False)
    how_they_found_out = forms.CharField(max_length=255, required=False)
    marital_status = forms.ChoiceField(choices=[('', '---------')] + list(MARITAL_STATUS_CHOICES), required=False)
    education_level = forms.ChoiceField(choices=[('', '---------')] + list(EDUCATION_LEVEL_CHOICES), required=False)
    occupation = forms.CharField(max_length=100, required=False)
    return_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'identification_number',
            'document_type', 'expedition_place', 'landline_phone',
            'residence_address', 'neighborhood', 'city', 'department', 'stratum',
            'phone_number', 'reception_medium', 'how_they_found_out',
            'marital_status', 'education_level', 'occupation', 'return_date',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        identification_number = self.cleaned_data['identification_number']
        user.username = identification_number
        user.set_password(identification_number)
        user.document_type = self.cleaned_data.get('document_type', '')
        user.expedition_place = self.cleaned_data.get('expedition_place', '')
        user.landline_phone = self.cleaned_data.get('landline_phone', '')
        user.neighborhood = self.cleaned_data.get('neighborhood', '')
        user.city = self.cleaned_data.get('city', '')
        user.department = self.cleaned_data.get('department', '')
        user.stratum = self.cleaned_data.get('stratum', '')
        user.reception_medium = self.cleaned_data.get('reception_medium', '')
        user.how_they_found_out = self.cleaned_data.get('how_they_found_out', '')
        user.marital_status = self.cleaned_data.get('marital_status', '')
        user.education_level = self.cleaned_data.get('education_level', '')
        user.occupation = self.cleaned_data.get('occupation', '')
        user.return_date = self.cleaned_data.get('return_date') or None

        if commit:
            user.save()

        return user
