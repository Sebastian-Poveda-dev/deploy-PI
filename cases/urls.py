from django.urls import path

from .views import (
    CaseApproveAPIView,
    CaseDetailAPIView,
    CaseListCreateAPIView,
    CaseRejectAssignmentAPIView,
)

urlpatterns = [
    path('', CaseListCreateAPIView.as_view(), name='case-list-create'),
    path('<int:pk>/', CaseDetailAPIView.as_view(), name='case-detail'),
    path('<int:pk>/approve/', CaseApproveAPIView.as_view(), name='case-approve'),
    path(
        '<int:pk>/reject-assignment/',
        CaseRejectAssignmentAPIView.as_view(),
        name='case-reject-assignment',
    ),
]
