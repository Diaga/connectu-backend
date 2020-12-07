from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from . import serializers
from .models import Question, Answer, Comment


class AuthTokenViewSet(ObtainAuthToken):
    """Custom token authentication view set"""

    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class QuestionDetailViewSet(viewsets.ModelViewSet):
    """Model view set for question model"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.QuestionSerializer

    queryset = Question.objects.all()

    def get_serializer_context(self):
        """Returning context"""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_queryset(self):
        """Enforcing Scope"""
        user = self.request.user
        queryset = super(QuestionDetailViewSet, self).get_queryset()
        if user.is_mentor:
            queryset.all()
            #TODO: filtering on the basis of keywords
        elif not user.is_mentor:
            queryset.filter(user=user).all()
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Updating keywords"""
        text = self.request.data.get('text')
        # TODO: use this text for converting to keywords
        serializer.save(user=self.request.user)


class AnswerDetailViewSet(viewsets.ModelViewSet):
    """Model view set for answer model"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.AnswerSerializer

    queryset = Answer.objects.all()

    def get_serializer_context(self):
        """Returning context"""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_queryset(self):
        """Enforcing Scope"""
        user = self.request.user
        queryset = super(AnswerDetailViewSet, self).get_queryset()
        if user.is_mentor:
            queryset.filter(user=user)
        elif not user.is_mentor:
            queryset.filter(question__user=user).all()
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Updating user"""
        question = Question.objects.filter(id=self.request.data.get("question")).first()
        serializer.save(user=self.request.user, question=question)


class CommentDetailViewSet(viewsets.ModelViewSet):
    """View set for comment model"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.CommentSerializer

    queryset = Comment.objects.all()

    def get_queryset(self):
        """Returning only related comments"""
        user = self.request.user
        queryset = super(CommentDetailViewSet, self).get_queryset()
        if user.is_mentor:
            queryset = queryset.filter(user=user) | queryset.filter(answer__user=user)
        elif not user.is_mentor:
            queryset.filter(user=user) | queryset.filter(answer__question__user=user)
        return queryset.order_by("-create_at")

    def perform_create(self, serializer):
        """Updating user"""
        answer = Answer.objects.filter(id=self.request.data.get("answer")).first()
        serializer.save(user=self.request.user, answer=answer)