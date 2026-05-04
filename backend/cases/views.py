from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CaseCreateForm
from .models import Case
from .serializers import (
	BeneficiaryCaseSerializer,
	CaseCancellationRequestSerializer,
	CaseCreateSerializer,
	CaseLogCreateSerializer,
	CaseLogSerializer,
	CaseSerializer,
	CaseUpdateSerializer,
	PublicBeneficiaryCaseStatusSerializer,
)
from .services import (
	approve_case,
	approve_cancellation_request,
	create_case,
	create_case_log,
	get_case_logs,
	reject_case_assignment,
	reject_cancellation_request,
	update_case,
)


PRIVILEGED_ROLES = {'admin', 'advisor'}


@login_required
@require_http_methods(['GET', 'POST'])
def case_create_form_view(request):
	form = CaseCreateForm(request.POST or None)

	if request.method == 'POST' and form.is_valid():
		try:
			create_case(
				request.user,
				description=form.cleaned_data['description'],
				category=form.cleaned_data['category'],
				subclinic=form.cleaned_data['subclinic'],
				beneficiary=form.cleaned_data['beneficiary'],
			)
		except (PermissionError, ValueError) as exc:
			form.add_error(None, str(exc))
		else:
			return redirect(f"{reverse('case-create-form')}?created=1")

	return render(
		request,
		'cases/case_form.html',
		{
			'form': form,
			'created': request.GET.get('created') == '1',
		},
	)


class CaseListCreateAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		role = request.user.groups.values_list('name', flat=True).first()
		if role == 'beneficiary':
			cases = Case.objects.filter(beneficiary=request.user)
			return Response(
				BeneficiaryCaseSerializer(cases, many=True).data,
				status=status.HTTP_200_OK,
			)
		if role in PRIVILEGED_ROLES:
			cases = Case.objects.all()
		else:
			cases = Case.objects.filter(assignments__user=request.user).distinct()
		return Response(CaseSerializer(cases, many=True).data, status=status.HTTP_200_OK)

	def post(self, request):
		serializer = CaseCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		try:
			case = create_case(request.user, **serializer.validated_data)
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(CaseSerializer(case).data, status=status.HTTP_201_CREATED)


class BeneficiaryCaseListAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		role = request.user.groups.values_list('name', flat=True).first()
		if role != 'beneficiary':
			return Response(
				{'detail': 'Only beneficiaries can view beneficiary cases.'},
				status=status.HTTP_403_FORBIDDEN,
			)

		cases = Case.objects.filter(beneficiary=request.user)
		if not cases.exists():
			return Response(
				{
					'detail': 'No tiene casos registrados',
					'cases': [],
				},
				status=status.HTTP_200_OK,
			)

		return Response(
			{'cases': BeneficiaryCaseSerializer(cases, many=True).data},
			status=status.HTTP_200_OK,
		)


class PublicBeneficiaryCaseTrackingAPIView(APIView):
	permission_classes = []
	authentication_classes = []

	def post(self, request):
		identification_number = str(request.data.get('identification_number', '')).strip()
		if not identification_number:
			return Response(
				{'detail': 'La cedula es requerida.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		cases = Case.objects.filter(
			beneficiary__identification_number=identification_number,
			beneficiary__groups__name='beneficiary',
		).distinct()

		if not cases.exists():
			return Response(
				{
					'detail': 'No tiene casos registrados',
					'cases': [],
				},
				status=status.HTTP_200_OK,
			)

		return Response(
			{'cases': PublicBeneficiaryCaseStatusSerializer(cases, many=True).data},
			status=status.HTTP_200_OK,
		)


class CaseDetailAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def _get_case(self, pk):
		return get_object_or_404(Case, pk=pk)

	def put(self, request, pk):
		return self._update(request, pk, partial=False)

	def patch(self, request, pk):
		return self._update(request, pk, partial=True)

	def _update(self, request, pk, partial):
		case = self._get_case(pk)
		serializer = CaseUpdateSerializer(data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)

		try:
			updated_case = update_case(case, request.user, serializer.validated_data)
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(CaseSerializer(updated_case).data, status=status.HTTP_200_OK)


class CaseApproveAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		case = get_object_or_404(Case, pk=pk)

		try:
			approved_case = approve_case(case, request.user)
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(CaseSerializer(approved_case).data, status=status.HTTP_200_OK)


class CaseRejectAssignmentAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		case = get_object_or_404(Case, pk=pk)

		try:
			reject_case_assignment(case, request.user)
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(
			{'detail': 'Case assignment rejected.'},
			status=status.HTTP_200_OK,
		)


class CaseLogListCreateAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, pk):
		case = get_object_or_404(Case, pk=pk)

		try:
			logs = get_case_logs(case, request.user)
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(
			CaseLogSerializer(logs, many=True, context={'request': request}).data,
			status=status.HTTP_200_OK,
		)

	def post(self, request, pk):
		case = get_object_or_404(Case, pk=pk)
		serializer = CaseLogCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		try:
			log = create_case_log(request.user, case, serializer.validated_data['content'])
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

		return Response(
			CaseLogSerializer(log, context={'request': request}).data,
			status=status.HTTP_201_CREATED,
		)


class CreateCancellationRequestAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		case = get_object_or_404(Case, pk=pk)
		
		is_assigned_student = case.users.filter(pk=request.user.pk, groups__name='student').exists()
		if not is_assigned_student:
			return Response({'detail': 'Only the assigned student can request cancellation.'}, status=status.HTTP_403_FORBIDDEN)
		
		serializer = CaseCancellationRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		
		if case.cancellation_requests.filter(status='pending').exists():
			return Response({'detail': 'A pending cancellation request already exists for this case.'}, status=status.HTTP_400_BAD_REQUEST)
			
		from .models import CaseCancellationRequest
		cancellation_request = CaseCancellationRequest.objects.create(
			case=case,
			requested_by=request.user,
			reason=serializer.validated_data['reason']
		)
		
		return Response(CaseCancellationRequestSerializer(cancellation_request).data, status=status.HTTP_201_CREATED)


class ReviewCancellationRequestAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, pk):
		from .models import CaseCancellationRequest
		cancellation_request = get_object_or_404(CaseCancellationRequest, pk=pk)
		
		action = request.data.get('action')
		
		try:
			if action == 'approve':
				result = approve_cancellation_request(cancellation_request, request.user)
			elif action == 'reject':
				result = reject_cancellation_request(cancellation_request, request.user)
			else:
				return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
		except PermissionError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
		except ValueError as exc:
			return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
			
		return Response(CaseCancellationRequestSerializer(result).data, status=status.HTTP_200_OK)


class ListCancellationRequestsAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		from .models import CaseCancellationRequest
		role = request.user.groups.values_list('name', flat=True).first()
		
		if role in PRIVILEGED_ROLES:
			queryset = CaseCancellationRequest.objects.all()
		elif role == 'professor':
			queryset = CaseCancellationRequest.objects.filter(case__users=request.user)
		elif role == 'student':
			queryset = CaseCancellationRequest.objects.filter(requested_by=request.user)
		else:
			queryset = CaseCancellationRequest.objects.none()
			
		return Response(CaseCancellationRequestSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
