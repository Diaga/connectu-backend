from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from . import serializers
from .models import Question, Answer


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
    """Model view set for question model"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.AnswerSerializer

    queryset = Answer.objects.all()

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
        """Updating keywords"""
        question = Question.objects.filter(id=self.request.data.get("question")).first()
        serializer.save(user=self.request.user, question=question)
