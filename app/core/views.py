from django.contrib.auth.models import AnonymousUser

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, status

from . import serializers
from .models import Question, Answer, Comment, Upvote, User, PairSession, Mentor


class AuthTokenViewSet(ObtainAuthToken):
    """Custom token authentication view set"""

    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class UserDetailViewSet(viewsets.ModelViewSet):

    authentication_classes = [TokenAuthentication, ]

    permission_classes = []

    serializer_class = serializers.UserSerializer

    queryset = User.objects.all()

    def get_serializer_context(self):
        """Returning context"""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_queryset(self):
        """Enforcing Scope"""
        queryset = super(UserDetailViewSet, self).get_queryset()
        is_me = self.request.GET.get('is_me', None)
        if is_me is not None and not isinstance(self.request.user, AnonymousUser):
            queryset = queryset.filter(
                email=self.request.user.email
            )
        return queryset


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
            # TODO: filtering on the basis of keywords
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


class UpvotesViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    """View set for upvote model"""
    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.UpvoteSerializer

    queryset = Upvote.objects.all()

    def get_queryset(self):
        """Getting required viewset"""
        user = self.request.user
        return super(UpvotesViewSet, self).get_queryset().filter(user=user)

    def get_object(self):
        """Getting the object to update"""
        queryset = self.get_queryset()
        answer_id = self.request.data.get("answer", None)
        question_id = self.request.data.get("question", None)
        if answer_id is not None:
            queryset.filter(answer__id=answer_id)
        elif question_id is not None:
            queryset.filter(question__id=question_id)
        else:
            return None
        return queryset.first()

    def create(self, request, *args, **kwargs):
        upvote = self.get_object()
        if upvote is not None:
            upvote.has_upvoted = self.request.data.get('has_upvoted')
            upvote.save()
            return Response("Upvote updated", status=status.HTTP_200_OK)
        else:
            return Response("Provide answer or question", status=status.HTTP_400_BAD_REQUEST)


class PairSessionViewSet(viewsets.GenericViewSet,
                         mixins.CreateModelMixin):
    """View set for pair session model"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.PairSessionSerializer

    queryset = PairSession.objects.all()

    def get_queryset(self):
        """Enforcing scope"""
        user = self.request.user
        queryset = super(PairSessionViewSet, self).get_queryset()
        if user.is_mentor:
            queryset.filter(mentor=user.mentor).all()
        else:
            queryset.filter(student=user.mentor).all()
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        mentor_id = self.request.data.get("mentor")
        serializer.save(student=self.request.user.student, mentor=Mentor.objects.filter(id=mentor_id).first())


