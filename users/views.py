from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def login_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'authenticated': False}, status=401)

    login(request, user)
    return JsonResponse({'authenticated': True}, status=200)
