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

from cases.models import Category

from .forms import BeneficiaryRegisterForm
from .services import admin_create_user, list_users, update_user

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
    return JsonResponse(
        {
            'id': request.user.id,
            'username': request.user.username,
            'role': role or '',
        }
    )


@require_GET
def professors_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    professors = User.objects.filter(groups__name='professor').values('id', 'username')
    return JsonResponse(list(professors), safe=False)


def _user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'role': user.groups.values_list('name', flat=True).first() or '',
        'is_active': user.is_active,
        'favorite_category_id': user.favorite_category_id,
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
        favorite_category_id = request.data.get('favorite_category_id', None)

        if not username or not password or not new_role:
            return Response(
                {'detail': 'username, password and role are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        favorite_category = None
        if favorite_category_id not in (None, ''):
            favorite_category = Category.objects.filter(pk=favorite_category_id).first()
            if favorite_category is None:
                return Response(
                    {'detail': 'favorite_category_id is invalid.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            user = admin_create_user(
                username,
                password,
                new_role,
                favorite_category=favorite_category,
            )
        except Group.DoesNotExist:
            return Response(
                {'detail': f"Role '{new_role}' does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(_user_to_dict(user), status=status.HTTP_201_CREATED)


class UserManagementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        target = get_object_or_404(User, pk=pk)

        payload = dict(request.data)
        if 'favorite_category_id' in request.data:
            favorite_category_id = request.data.get('favorite_category_id')
            if favorite_category_id in (None, ''):
                payload['favorite_category'] = None
            else:
                favorite_category = Category.objects.filter(pk=favorite_category_id).first()
                if favorite_category is None:
                    return Response(
                        {'detail': 'favorite_category_id is invalid.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                payload['favorite_category'] = favorite_category
            payload.pop('favorite_category_id', None)

        try:
            user = update_user(request.user, target, payload)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except (ValueError, Group.DoesNotExist) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(_user_to_dict(user))


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
