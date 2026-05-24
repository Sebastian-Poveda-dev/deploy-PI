from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services

ALLOWED_ROLES = {'admin', 'advisor'}


def _check_permission(request):
    return request.user.groups.filter(name__in=ALLOWED_ROLES).exists()


class MetricsDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _check_permission(request):
            return Response({'detail': 'Permission denied.'}, status=403)

        return Response({
            'cases_by_status': services.get_cases_by_status(),
            'cases_by_category': services.get_cases_by_category(),
            'cases_by_subclinic': services.get_cases_by_subclinic(),
            'working_velocity': services.get_working_velocity(),
            'avg_resolution_time': services.get_avg_resolution_time(),
            'opened_vs_closed': services.get_opened_vs_closed(),
            'cases_per_user': services.get_cases_per_user(),
            'unassigned_cases': services.get_unassigned_cases(),
            'cancellation_rate': services.get_cancellation_rate(),
            'document_expiration': services.get_document_expiration(),
        })


class StudentCaseSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _check_permission(request):
            return Response({'detail': 'Permission denied.'}, status=403)

        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([])

        return Response(services.search_student_cases(query))
