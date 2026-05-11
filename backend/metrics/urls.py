from django.urls import path

from .views import MetricsDashboardAPIView

urlpatterns = [
    path('', MetricsDashboardAPIView.as_view(), name='metrics-dashboard'),
]
