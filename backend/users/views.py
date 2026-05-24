import json

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import BeneficiaryRegisterForm
from .services import admin_create_user, change_own_password, list_users, update_beneficiary_info, update_user

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
    role = user.groups.values_list('name', flat=True).first()
    return JsonResponse({'authenticated': True, 'role': role or ''}, status=200)


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

    extra_info_raw = request.POST.get('extra_info', '').strip()
    if extra_info_raw:
        try:
            extra_info = json.loads(extra_info_raw)
            if isinstance(extra_info, dict):
                user.extra_info = extra_info
                user.save(update_fields=['extra_info'])
        except json.JSONDecodeError:
            pass

    beneficiary_group = Group.objects.get(name='beneficiary')
    user.groups.add(beneficiary_group)
    return JsonResponse({'registered': True}, status=201)


def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    role = request.user.groups.values_list('name', flat=True).first()
    return JsonResponse(
        {
            'id': request.user.id,
            'username': request.user.username,
            'role': role or '',
        }
    )


@require_POST
@csrf_exempt
def change_password_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    try:
        import json as _json
        body = _json.loads(request.body)
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON.'}, status=400)

    current_password = body.get('current_password', '')
    new_password = body.get('new_password', '')

    try:
        change_own_password(request.user, current_password, new_password)
    except ValueError as exc:
        return JsonResponse({'detail': str(exc)}, status=400)

    return JsonResponse({'detail': 'Contraseña actualizada correctamente.'}, status=200)


def _user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.groups.values_list('name', flat=True).first() or '',
        'is_active': user.is_active,
        'category_id': user.category_id,
        'category_name': user.category.name if user.category_id else '',
    }


def _full_user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'identification_number': user.identification_number or '',
        'document_type': user.document_type or '',
        'expedition_place': user.expedition_place or '',
        'landline_phone': user.landline_phone or '',
        'residence_address': user.residence_address or '',
        'neighborhood': user.neighborhood or '',
        'city': user.city or '',
        'department': user.department or '',
        'stratum': user.stratum or '',
        'phone_number': user.phone_number or '',
        'reception_medium': user.reception_medium or '',
        'how_they_found_out': user.how_they_found_out or '',
        'marital_status': user.marital_status or '',
        'education_level': user.education_level or '',
        'occupation': user.occupation or '',
        'return_date': str(user.return_date) if user.return_date else '',
        'extra_info': user.extra_info or {},
        'role': user.groups.values_list('name', flat=True).first() or '',
        'is_active': user.is_active,
    }


class UserManagementListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            users = list_users(request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response([_user_to_dict(u) for u in users])

    def post(self, request):
        role = request.user.groups.values_list('name', flat=True).first()
        if role != 'admin':
            return Response({'detail': 'Only admins can create users.'}, status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        new_role = request.data.get('role', '').strip()

        if not username or not password or not new_role:
            return Response(
                {'detail': 'username, password and role are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        category_id = request.data.get('category_id') or None
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()

        try:
            user = admin_create_user(username, password, new_role, first_name=first_name, last_name=last_name, category_id=category_id)
        except Group.DoesNotExist:
            return Response(
                {'detail': f"Role '{new_role}' does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(_user_to_dict(user), status=status.HTTP_201_CREATED)


BENEFICIARY_CONTACT_FIELDS = {
    'first_name', 'last_name', 'email', 'identification_number',
    'document_type', 'expedition_place', 'landline_phone',
    'residence_address', 'neighborhood', 'city', 'department', 'stratum',
    'phone_number', 'reception_medium', 'how_they_found_out',
    'marital_status', 'education_level', 'occupation', 'return_date',
    'extra_info',
}


class UserManagementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        return Response(_full_user_to_dict(target))

    def patch(self, request, pk):
        target = get_object_or_404(User, pk=pk)

        if any(k in request.data for k in BENEFICIARY_CONTACT_FIELDS):
            try:
                user = update_beneficiary_info(request.user, target, dict(request.data))
            except PermissionError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
            except ValueError as exc:
                return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(_full_user_to_dict(user))

        try:
            user = update_user(request.user, target, dict(request.data))
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except (ValueError, Group.DoesNotExist) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_user_to_dict(user))

@require_GET
def staff_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    users = User.objects.filter(
        groups__name__in=['advisor', 'student'],
        is_active=True,
    ).distinct().order_by('username')

    return JsonResponse(
        [{'id': u.id, 'username': u.username, 'role': u.groups.values_list('name', flat=True).first()} for u in users],
        safe=False,
    )


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


@require_GET
def beneficiaries_detail_view(request):
    """
    Returns beneficiaries with their contact info and cases.
    Admin: all beneficiaries.
    Advisor / student: only beneficiaries whose cases they are assigned to.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    from cases.models import Case

    role = request.user.groups.values_list('name', flat=True).first()

    if role == 'admin':
        beneficiaries = User.objects.filter(groups__name='beneficiary').order_by('first_name', 'last_name')
    elif role in {'advisor', 'student'}:
        assigned_case_ids = request.user.case_assignments.values_list('case_id', flat=True)
        beneficiary_ids = Case.objects.filter(pk__in=assigned_case_ids).values_list('beneficiary_id', flat=True).distinct()
        beneficiaries = User.objects.filter(pk__in=beneficiary_ids).order_by('first_name', 'last_name')
    else:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    data = []
    for b in beneficiaries:
        cases = Case.objects.filter(beneficiary=b).select_related('status', 'category', 'subclinic')
        if role in {'advisor', 'student'}:
            assigned_case_ids_set = set(request.user.case_assignments.values_list('case_id', flat=True))
            cases = cases.filter(pk__in=assigned_case_ids_set)

        full_name = f'{b.first_name} {b.last_name}'.strip() or b.username
        data.append({
            'id': b.id,
            'full_name': full_name,
            'username': b.username,
            'email': b.email or '',
            'identification_number': b.identification_number or '',
            'phone_number': b.phone_number or '',
            'residence_address': b.residence_address or '',
            'cases': [
                {
                    'id': c.id,
                    'status': c.status.name,
                    'category': c.category.name if c.category_id else '',
                    'subclinic': c.subclinic.name if c.subclinic_id else '',
                }
                for c in cases
            ],
        })
    return JsonResponse(data, safe=False)
