from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cases.models import Case

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .services import download_document, get_case_documents, upload_document


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
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


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
