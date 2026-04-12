from django.urls import path

from documents.views import CaseDocumentListCreateAPIView

from .views import (
    CaseApproveAPIView,
    CaseDetailAPIView,
    CaseLogListCreateAPIView,
    CaseListCreateAPIView,
    CaseRejectAssignmentAPIView,
)

urlpatterns = [
    path('', CaseListCreateAPIView.as_view(), name='case-list-create'),
    path('<int:pk>/', CaseDetailAPIView.as_view(), name='case-detail'),
    path('<int:pk>/approve/', CaseApproveAPIView.as_view(), name='case-approve'),
    path('<int:pk>/documents/', CaseDocumentListCreateAPIView.as_view(), name='case-documents'),
    path('<int:pk>/logs/', CaseLogListCreateAPIView.as_view(), name='case-logs'),
    path(
        '<int:pk>/reject-assignment/',
        CaseRejectAssignmentAPIView.as_view(),
        name='case-reject-assignment',
    ),
]
