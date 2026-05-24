from django.urls import path

from .views import (
    beneficiaries_view,
    beneficiaries_detail_view,
    change_password_view,
    staff_view,
    login_view,
    me_view,
    register_view,
    UserManagementListCreateView,
    UserManagementDetailView,
)

app_name = 'users'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('me/', me_view, name='me'),
    path('me/change-password/', change_password_view, name='change-password'),
    path('', UserManagementListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', UserManagementDetailView.as_view(), name='user-detail'),
    path('staff/', staff_view, name='staff'),
    path('beneficiaries/', beneficiaries_view, name='beneficiaries'),
    path('beneficiaries/detail/', beneficiaries_detail_view, name='beneficiaries-detail'),
]
