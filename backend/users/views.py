from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

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


def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    role = request.user.groups.values_list('name', flat=True).first()
    return JsonResponse({
        'id': request.user.id,
        'username': request.user.username,
        'role': role or '',
    })


@require_GET
def professors_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    professors = User.objects.filter(groups__name='professor').values('id', 'username')
    return JsonResponse(list(professors), safe=False)


@require_GET
def beneficiaries_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    users = User.objects.filter(groups__name='beneficiary').order_by('first_name', 'last_name')
    data = []
    for user in users:
        full_name = f'{user.first_name} {user.last_name}'.strip() or user.username
        data.append(
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': full_name,
            }
        )
    return JsonResponse(data, safe=False)
