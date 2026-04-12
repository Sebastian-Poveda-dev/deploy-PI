from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.conf import settings
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import BeneficiaryRegisterForm

User = apps.get_model(settings.AUTH_USER_MODEL)


@require_POST
@csrf_exempt
def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'authenticated': False}, status=401)

    login(request, user)
    return JsonResponse({'authenticated': True}, status=200)


@require_POST
@csrf_exempt
def register_view(request):
    form = BeneficiaryRegisterForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {'registered': False, 'errors': form.errors.get_json_data()},
            status=400,
        )

    user = form.save()
    beneficiary_group = Group.objects.get(name='beneficiary')
    user.groups.add(beneficiary_group)
    return JsonResponse({'registered': True}, status=201)
