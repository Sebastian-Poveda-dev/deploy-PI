from django.urls import path

from .views import DocumentDownloadAPIView, DocumentNotificationListAPIView

app_name = 'documents'

urlpatterns = [
    path('notifications/', DocumentNotificationListAPIView.as_view(), name='document-notifications'),
    path('<int:pk>/download/', DocumentDownloadAPIView.as_view(), name='document-download'),
]
