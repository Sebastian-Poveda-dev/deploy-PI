from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case

from .models import Document
from .serializers import (
    DocumentExpirationNotificationSerializer,
    DocumentExpirationVerificationSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
)
from .services import (
    download_document,
    get_case_documents,
    get_user_document_notifications,
    upload_document,
    verify_document_expirations,
)


DOCUMENT_EXPIRATION_TRIGGER_ALLOWED_ROLES = {'admin', 'advisor'}


class CaseDocumentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        case = get_object_or_404(Case, pk=pk)

        try:
            documents = get_case_documents(case, request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            DocumentSerializer(documents, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        case = get_object_or_404(Case, pk=pk)
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            document = upload_document(
                case=case,
                user=request.user,
                file=request.FILES['file'],
                **{
                    key: value
                    for key, value in serializer.validated_data.items()
                    if key != 'file'
                },
            )
            return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DocumentDownloadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            return download_document(pk, request.user)
        except Document.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class DocumentNotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = get_user_document_notifications(request.user)
        return Response(
            DocumentExpirationNotificationSerializer(notifications, many=True).data,
            status=status.HTTP_200_OK,
        )


class DocumentExpirationVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = request.user.groups.values_list('name', flat=True).first()
        if role not in DOCUMENT_EXPIRATION_TRIGGER_ALLOWED_ROLES:
            return Response(
                {'detail': 'Only admins and advisors can trigger expiration verification.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DocumentExpirationVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notifications = verify_document_expirations(
            today=serializer.validated_data.get('today'),
            alert_days=serializer.validated_data.get('alert_days'),
        )
        processed_date = serializer.validated_data.get('today') or date.today()

        return Response(
            {
                'created_notifications': len(notifications),
                'processed_date': str(processed_date),
            },
            status=status.HTTP_200_OK,
        )
