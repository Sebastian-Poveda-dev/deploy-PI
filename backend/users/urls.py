from django.urls import path

from .views import beneficiaries_view, login_view, me_view, professors_view, register_view

app_name = 'users'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('me/', me_view, name='me'),
    path('professors/', professors_view, name='professors'),
    path('beneficiaries/', beneficiaries_view, name='beneficiaries'),
]