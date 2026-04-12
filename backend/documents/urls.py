from django.urls import path

from .views import DocumentDownloadAPIView

app_name = 'documents'

urlpatterns = [
    path('<int:pk>/download/', DocumentDownloadAPIView.as_view(), name='document-download'),
]
