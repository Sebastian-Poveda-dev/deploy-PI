from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ChatUserSerializer,
    ConversationCreateSerializer,
    ConversationSerializer,
    MessageCreateSerializer,
    MessageSerializer,
)
from .services import (
    create_conversation,
    create_message,
    list_chat_users,
    list_conversations_for_user,
    list_messages,
)


class SessionAuthentication401(SessionAuthentication):
    def authenticate_header(self, request):
        return 'Session'


class AuthenticatedChatAPIView(APIView):
    authentication_classes = [SessionAuthentication401]
    permission_classes = [IsAuthenticated]


class ChatUserListAPIView(AuthenticatedChatAPIView):
    def get(self, request):
        users = list_chat_users(request.user)
        return Response(ChatUserSerializer(users, many=True).data, status=status.HTTP_200_OK)


class ConversationListCreateAPIView(AuthenticatedChatAPIView):
    def get(self, request):
        conversations = list_conversations_for_user(request.user)
        return Response(
            ConversationSerializer(conversations, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            conversation = create_conversation(
                creator=request.user,
                participant_ids=serializer.validated_data['participant_ids'],
                title=serializer.validated_data.get('title', ''),
            )
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ConversationSerializer(conversation, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class MessageListCreateAPIView(AuthenticatedChatAPIView):
    def get(self, request, pk):
        try:
            messages = list_messages(request.user, pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(
            MessageSerializer(messages, many=True, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            message = create_message(
                user=request.user,
                conversation_id=pk,
                content=serializer.validated_data['content'],
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            MessageSerializer(message, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
