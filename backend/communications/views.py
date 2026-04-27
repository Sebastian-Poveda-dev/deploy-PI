from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation
from .serializers import (
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)
from .services import (
    create_conversation,
    create_message,
    list_conversations_for_user,
    list_messages,
)


class ConversationListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = list_conversations_for_user(request.user)
        return Response(
            ConversationSerializer(conversations, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = create_conversation(
                creator=request.user,
                beneficiary=serializer.validated_data['beneficiary'],
                channel=serializer.validated_data['channel'],
            )
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ConversationSerializer(conversation).data,
            status=status.HTTP_201_CREATED,
        )


class MessageListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_conversation(self, pk):
        return get_object_or_404(
            Conversation.objects.select_related('creator', 'beneficiary'),
            pk=pk,
        )

    def get(self, request, pk):
        conversation = self.get_conversation(pk)

        try:
            messages = list_messages(conversation, request.user)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            MessageSerializer(messages, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        conversation = self.get_conversation(pk)
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = create_message(
                conversation=conversation,
                sender=request.user,
                content=serializer.validated_data['content'],
            )
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            MessageSerializer(message, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
