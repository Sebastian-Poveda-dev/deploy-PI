from django.urls import path

from .views import (
    DocumentDownloadAPIView,
    DocumentExpirationVerificationAPIView,
    DocumentNotificationListAPIView,
)

app_name = 'documents'

urlpatterns = [
    path(
        'notifications/check/',
        DocumentExpirationVerificationAPIView.as_view(),
        name='document-notifications-check',
    ),
    path('notifications/', DocumentNotificationListAPIView.as_view(), name='document-notifications'),
    path('<int:pk>/download/', DocumentDownloadAPIView.as_view(), name='document-download'),
]
