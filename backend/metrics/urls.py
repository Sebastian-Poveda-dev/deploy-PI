from django.urls import path

from .views import MetricsDashboardAPIView, StudentCaseSearchAPIView

urlpatterns = [
    path('', MetricsDashboardAPIView.as_view(), name='metrics-dashboard'),
    path('user-cases/', StudentCaseSearchAPIView.as_view(), name='user-case-search'),
]
