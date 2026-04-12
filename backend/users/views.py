from django.contrib.auth import authenticate, login
from django.conf import settings
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .services import register_beneficiary

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
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    residence_address = request.POST.get('residence_address', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()

    if not username or not password or not residence_address or not phone_number:
        return JsonResponse({'registered': False, 'error': 'Missing required fields'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'registered': False, 'error': 'Username already exists'}, status=400)

    register_beneficiary(username, password, residence_address, phone_number)
    return JsonResponse({'registered': True}, status=201)
