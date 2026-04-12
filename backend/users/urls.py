from django.urls import path

from .views import (
    login_view,
    me_view,
    professors_view,
    register_view,
    UserManagementListCreateView,
    UserManagementDetailView,
)

app_name = 'users'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('me/', me_view, name='me'),
    path('professors/', professors_view, name='professors'),
    path('', UserManagementListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserManagementDetailView.as_view(), name='user-detail'),
]
