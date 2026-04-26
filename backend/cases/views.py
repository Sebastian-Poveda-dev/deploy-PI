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
	CaseCreateSerializer,
	CaseLogCreateSerializer,
	CaseLogSerializer,
	CaseSerializer,
	CaseUpdateSerializer,
)
from .services import (
	approve_case,
	create_case,
	create_case_log,
	get_case_logs,
	reject_case_assignment,
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
		return Response(CaseSerializer(cases, many=True).data, status=status.HTTP_200_OK)


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
