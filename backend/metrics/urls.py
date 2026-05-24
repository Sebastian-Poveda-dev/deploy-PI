from django.urls import path

from .views import MetricsDashboardAPIView, StudentCaseSearchAPIView

urlpatterns = [
    path('', MetricsDashboardAPIView.as_view(), name='metrics-dashboard'),
    path('student-cases/', StudentCaseSearchAPIView.as_view(), name='student-case-search'),
]
