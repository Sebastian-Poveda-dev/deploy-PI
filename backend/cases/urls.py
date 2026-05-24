from django.urls import path

from documents.views import CaseDocumentListCreateAPIView

from .views import (
    BeneficiaryCaseListAPIView,
    CancellationRequestNotificationListAPIView,
    CancellationRequestNotificationMarkReadAPIView,
    CaseApproveAPIView,
    CaseCancelAPIView,
    CaseDetailAPIView,
    CaseLogListCreateAPIView,
    CaseListCreateAPIView,
    CaseProgressStatusListCreateAPIView,
    CaseRejectAssignmentAPIView,
    CategoryListAPIView,
    SubclinicListAPIView,
    PublicBeneficiaryCaseTrackingAPIView,
    case_create_form_view,
    CreateCancellationRequestAPIView,
    ReviewCancellationRequestAPIView,
    ListCancellationRequestsAPIView,
)

urlpatterns = [
    path('create/', case_create_form_view, name='case-create-form'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('subclinics/', SubclinicListAPIView.as_view(), name='subclinic-list'),
    path('track/', PublicBeneficiaryCaseTrackingAPIView.as_view(), name='public-beneficiary-case-track'),
    path('beneficiary/', BeneficiaryCaseListAPIView.as_view(), name='beneficiary-case-list'),
    path('', CaseListCreateAPIView.as_view(), name='case-list-create'),
    path('cancellation-requests/', ListCancellationRequestsAPIView.as_view(), name='cancellation-request-list'),
    path('cancellation-request-notifications/', CancellationRequestNotificationListAPIView.as_view(), name='cancellation-request-notifications'),
    path('cancellation-request-notifications/<int:pk>/read/', CancellationRequestNotificationMarkReadAPIView.as_view(), name='cancellation-request-notification-read'),
    path('cancellation-requests/<int:pk>/review/', ReviewCancellationRequestAPIView.as_view(), name='cancellation-request-review'),
    path('<int:pk>/', CaseDetailAPIView.as_view(), name='case-detail'),
    path('<int:pk>/approve/', CaseApproveAPIView.as_view(), name='case-approve'),
    path('<int:pk>/cancel/', CaseCancelAPIView.as_view(), name='case-cancel'),
    path('<int:pk>/documents/', CaseDocumentListCreateAPIView.as_view(), name='case-documents'),
    path('<int:pk>/logs/', CaseLogListCreateAPIView.as_view(), name='case-logs'),
    path('<int:pk>/progress-statuses/', CaseProgressStatusListCreateAPIView.as_view(), name='case-progress-statuses'),
    path('<int:pk>/request-cancellation/', CreateCancellationRequestAPIView.as_view(), name='case-request-cancellation'),
    path(
        '<int:pk>/reject-assignment/',
        CaseRejectAssignmentAPIView.as_view(),
        name='case-reject-assignment',
    ),
]
