from django.contrib.auth.models import AnonymousUser
from django.db.models import Count

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, status

from . import serializers
from .models import Question, Answer, Comment, Upvote, \
    User, PairSession, Mentor, FeedbackForm, Appointment, Degree, Student, Keyword, University, Notification

import uuid


class UniversityViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin):
    """Returning the list of universities"""
    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.UniversitySerializer

    queryset = University.objects.all()


class AuthTokenViewSet(ObtainAuthToken):
    """Custom token authentication view set"""

    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class DegreeDetailViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, ]

    permission_classes = []

    serializer_class = serializers.DegreeSerializer

    queryset = Degree.objects.all()

    def get_serializer_context(self):
        """Returning context"""
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }


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
        question = Question.objects.filter(id=self.request.data.get('question')).first()
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
        return queryset.order_by('-create_at')

    def perform_create(self, serializer):
        """Updating user"""
        answer = Answer.objects.filter(id=self.request.data.get('answer')).first()
        serializer.save(user=self.request.user, answer=answer)


class UpvotesViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    """View set for upvote model"""
    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.UpvoteSerializer

    queryset = Upvote.objects.all()

    is_answer = False

    def get_queryset(self):
        """Getting required viewset"""
        user = self.request.user
        return super(UpvotesViewSet, self).get_queryset().filter(user=user)

    def get_object(self):
        """Getting the object to update"""
        queryset = self.get_queryset()
        answer_id = self.request.data.get('answer', None)
        question_id = self.request.data.get('question', None)
        if answer_id is not None:
            self.is_answer = True
            queryset = queryset.filter(answer__id=answer_id)
        elif question_id is not None:
            queryset = queryset.filter(question__id=question_id)
        else:
            return None
        return queryset.first()

    def create(self, request, *args, **kwargs):
        upvote = self.get_object()
        if upvote is not None:
            upvote.has_upvoted = self.request.data.get('has_upvoted')
            if self.is_answer:
                user = upvote.answer.user
            else:
                user = upvote.question.user

            if upvote.has_upvoted:
                if user.is_mentor:
                    user.mentor.points += 5
                    user.mentor.save()

            upvote.save()
            return Response('Upvote updated', status=status.HTTP_200_OK)
        else:
            return Response('Provide answer or question', status=status.HTTP_400_BAD_REQUEST)


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
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        mentor_id = self.request.data.get('mentor')
        serializer.save(
            student=self.request.user.student,
            mentor=Mentor.objects.filter(id=mentor_id).first()
        )


class FeedbackFormViewSet(viewsets.GenericViewSet,
                          mixins.CreateModelMixin):
    """Update feedback form after paired session"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.FeedbackFormSerializer

    queryset = FeedbackForm.objects.all()

    def get_object(self):
        """Getting the object to update"""
        feedback_form_id = self.request.data.get('feedback_form')
        if feedback_form_id is not None:
            return FeedbackForm.objects.get(id=feedback_form_id)
        else:
            return None

    def create(self, request, *args, **kwargs):
        feedback_obj = self.get_object()
        if feedback_obj is not None:

            student_satisfied_rating = self.request.data.get('student_satisfied_rating', None)
            mentor_satisfied_rating = self.request.data.get('mentor_satisfied_rating', None)
            has_student_reported = self.request.data.get('has_student_reported', None)
            has_mentor_reported = self.request.data.get('has_mentor_reported', None)
            student_comment = self.request.data.get('student_comment', None)
            mentor_comment = self.request.data.get('mentor_comment', None)
            if student_satisfied_rating is not None:
                feedback_obj.student_satisfied_rating = student_satisfied_rating
            if mentor_satisfied_rating is not None:
                feedback_obj.mentor_satisfied_rating = mentor_satisfied_rating
            if has_student_reported is not None:
                feedback_obj.has_student_reported = has_student_reported
            if has_mentor_reported is not None:
                feedback_obj.has_mentor_reported = has_mentor_reported
            if student_comment is not None:
                feedback_obj.student_comment = student_comment
            if mentor_comment is not None:
                feedback_obj.mentor_comment = mentor_comment

            user = self.request.user
            if user.is_mentor:
                pair_session = PairSession.objects.filter(feedback_session=feedback_obj).first()
                Notification.objects.create(
                    user=pair_session.student.user,
                    title=f'Give feedback form for mentoring session with {user.name}',
                    feedback_form=feedback_obj
                )
            feedback_obj.save()
            return Response('Feedback form updated', status=status.HTTP_200_OK)
        else:
            return Response('Provide feedback form id', status=status.HTTP_400_BAD_REQUEST)


class AppointmentViewSet(viewsets.GenericViewSet,
                         mixins.CreateModelMixin,
                         mixins.ListModelMixin):
    """View set for appointment model"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.AppointmentSerializer

    queryset = Appointment.objects.all()

    def get_queryset(self):
        """Enforcing scope"""
        user = self.request.user
        queryset = super(AppointmentViewSet, self).get_queryset()
        if user.is_mentor:
            queryset.filter(mentor=user.mentor).all()
        else:
            queryset.filter(student=user.mentor).all()
        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Overriding create method for custom response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mentor_id = self.request.data.get('mentor')
        mentor = Mentor.objects.filter(id=mentor_id).first()
        if mentor is not None:
            if mentor.is_professional:
                serializer.save(
                    student=self.request.user.student,
                    mentor=mentor, url=f'meet.jit.si/connectu.ml/{str(uuid.uuid4())}',
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'Message': 'Cannot register appointment'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Message': 'Provide mentor id'},
                            status=status.HTTP_400_BAD_REQUEST)


class AboutMeViewSet(viewsets.GenericViewSet,
                     mixins.UpdateModelMixin):
    """View set for assigning top 3 degrees based on the test"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.DegreeSerializer

    queryset = Student.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = super(AboutMeViewSet, self).get_queryset().filter(id=user.student.id)
        return queryset

    def update(self, request, *args, **kwargs):
        """Updating student model for the required degrees"""
        about_me_text_1 = self.request.data.get("about_me_1").split(" ")
        about_me_text_2 = self.request.data.get("about_me_2").split(" ")
        about_me_text_3 = self.request.data.get("about_me_3").split(" ")
        result = {}
        for word in about_me_text_1:
            keywords = Keyword.objects.filter(name__icontains=word). \
                           values("degree").annotate(total=Count('id')).order_by('-total')[:3]
            for k in keywords:
                if str(k['degree']) not in result:
                    result[str(k['degree'])] = k['total']
                else:
                    result[str(k['degree'])] += k['total']
        for word in about_me_text_2:
            keywords = Keyword.objects.filter(name__icontains=word). \
                           values("degree").annotate(total=Count('id')).order_by('-total')[:3]
            for k in keywords:
                if str(k['degree']) not in result:
                    result[str(k['degree'])] = k['total']
                else:
                    result[str(k['degree'])] += k['total']
        for word in about_me_text_3:
            keywords = Keyword.objects.filter(name__icontains=word). \
                           values("degree").annotate(total=Count('id')).order_by('-total')[:3]
            for k in keywords:
                if str(k['degree']) not in result:
                    result[str(k['degree'])] = k['total']
                else:
                    result[str(k['degree'])] += k['total']
        sorted(result.values())
        degrees_id_list = list(result.keys())
        deg = Degree.objects.filter(id__in=degrees_id_list).all()[:3]
        if len(degrees_id_list) < 3:
            deg = Degree.objects.all().order_by("?")[:3]
        serializer = self.get_serializer(deg, many=True)
        student = self.get_queryset().first()
        student.degree1 = deg[0]
        student.degree2 = deg[1]
        student.degree3 = deg[2]
        student.save()
        return Response(serializer.data)


class MentorPairStudentViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin):
    """Return a mentor pair for student"""
    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.UserSerializer

    queryset = User.objects.filter(mentor__isnull=False)

    def get_queryset(self):
        """Enforcing scope"""
        user = self.request.user
        queryset = super(MentorPairStudentViewSet, self).get_queryset()
        if user.is_mentor:
            return None
        else:
            degree_id_1 = self.request.data.get('degree1', None)
            degree_id_2 = self.request.data.get('degree2', None)
            degree_id_3 = self.request.data.get('degree3', None)
            if degree_id_1 is not None:
                mentor_1 = queryset.filter(mentor__degree__id=degree_id_1).all().order_by('?')[:1]
            if degree_id_2 is not None:
                mentor_2 = queryset.filter(mentor__degree__id=degree_id_2).all().order_by('?')[:1]
            if degree_id_3 is not None:
                mentor_3 = queryset.filter(mentor__degree__id=degree_id_3).all().order_by('?')[:1]
            queryset = mentor_1 | mentor_2 | mentor_3

            return queryset


class NotificationViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.UpdateModelMixin):
    """Model view set for notifications"""

    authentication_classes = [TokenAuthentication, ]

    permission_classes = [IsAuthenticated, ]

    serializer_class = serializers.NotificationSerializer

    queryset = Notification.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = super(NotificationViewSet, self).get_queryset(). \
            filter(user=user). \
            order_by('-created_at', 'is_seen')
        return queryset

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(NotificationViewSet, self).update(request, *args, **kwargs)
