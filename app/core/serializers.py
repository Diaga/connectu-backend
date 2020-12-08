from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import User, Mentor, Student, Degree, \
    University, Question, Answer, Comment, Upvote, \
    PairSession, FeedbackForm, Appointment

class DegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Degree
        fields = ('id', 'name')
        read_only_fields = ('id',)


class UniversitySerializer(serializers.ModelSerializer):
    degrees = DegreeSerializer(many=True, read_only=True)

    class Meta:
        model = University
        fields = ('id', 'name', 'location', 'degrees')


class MentorSerializer(serializers.ModelSerializer):
    degree = DegreeSerializer()
    university = UniversitySerializer()

    class Meta:
        model = Mentor
        fields = ('id', 'is_professional', 'points',
                  'degree', 'university')
        read_only_fields = ('id', 'points',)

    def create(self, validated_data):

        degree = validated_data.pop('degree', None)
        university = validated_data.pop('university', None)

        if degree is not None:
            validated_data['degree'] = Degree.objects.create(**degree)

        if university is not None:
            validated_data['university'] = University.objects.create(**university)

        mentor = super(MentorSerializer, self).create(validated_data)

        mentor.save()

        return mentor

    def update(self, instance, validated_data):

        degree = validated_data.pop('degree', None)
        university = validated_data.pop('university', None)

        mentor = super(MentorSerializer, self).update(instance, validated_data)

        if degree is not None:
            degree_serializer = DegreeSerializer(data=degree, instance=Degree.objects.get(pk=degree['id']))
            if degree_serializer.is_valid(raise_exception=True):
                degree_serializer.save()

        if university is not None:
            university_serializer = UniversitySerializer(data=degree,
                                                         instance=University.objects.get(pk=university['id']))
            if university_serializer.is_valid(raise_exception=True):
                university_serializer.save()

        mentor.save()

        return mentor


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id',)
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True,
        min_length=5
    )

    mentor = MentorSerializer(required=False)
    student = StudentSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'mentor', 'student', 'is_mentor')
        read_only_fields = ('id',)

    def create(self, validated_data):

        mentor = validated_data.pop('mentor', None)
        student = validated_data.pop('student', None)

        if mentor is not None and student is not None:
            raise ValueError('A user cannot be both mentor and student!')

        user = User.objects.create_user(**validated_data)

        if mentor is not None:
            mentor_serializer = MentorSerializer(data=mentor)
            if mentor_serializer.is_valid(raise_exception=True):
                user.mentor = mentor_serializer.save(user=user)
        elif student is not None:
            user.student = Student.objects.create(**student, user=user)

        user.save()

        return user

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        mentor = validated_data.pop('mentor', None)
        student = validated_data.pop('student', None)

        user = super(UserSerializer, self).update(instance, validated_data)

        if password is not None:
            user.set_password(password)
            user.save()

        if mentor is not None and user.is_mentor:
            serializer = MentorSerializer(user.mentor, data=mentor)
            serializer.save()

        elif student is not None and not user.is_mentor:
            serializer = StudentSerializer(user.student, data=student)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Custom token authentication serializer"""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Authenticate and return user"""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class MinQuestionSerializer(serializers.ModelSerializer):
    """Serializer for question model to be returned along answer"""
    user = serializers.SerializerMethodField('get_user')

    def get_user(self, obj):
        """Returning the related user"""
        return UserSerializer(obj.user).data

    class Meta:
        model = Question
        fields = ('id', 'title', 'user')


class MinAnswerSerializer(serializers.ModelSerializer):
    """Serializer for answer model to be returned along questions"""
    user = serializers.SerializerMethodField('get_user')

    def get_user(self, obj):
        """Returning the related user"""
        return UserSerializer(obj.user).data

    class Meta:
        model = Answer
        fields = ('id', 'text', 'user',)
        read_only_fields = ('id',)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for question model"""
    user = serializers.SerializerMethodField('get_user')
    answers = serializers.SerializerMethodField('get_answers')
    is_upvoted = serializers.SerializerMethodField('get_is_upvoted')

    def get_answers(self, obj):
        """Returning the related answers"""
        answers = Answer.objects.filter(question=obj)
        if answers.count() > 0:
            return MinAnswerSerializer(answers, many=True).data
        else:
            return None

    def get_user(self, obj):
        """Returning the related user"""
        return UserSerializer(obj.user).data

    def get_is_upvoted(self, obj):
        """Return if the current user has upvoted"""
        user = self.context['request'].user
        upvote_query = obj.upvotes.filter(user=user)
        if not upvote_query.exists():
            obj.upvotes.add(Upvote.objects.create(user=user, question=obj, has_upvoted=False))
        return obj.upvotes.filter(user=user).first().has_upvoted

    # def get_keyword(self, obj):
    #     """Returning the list of associated keywords"""
    #     return KeywordSerializer(obj.keywords.all(), many=True).data

    class Meta:
        model = Question
        fields = ('id', 'title', 'text', 'created_at',
                  'user', 'answers', 'upvotes_count',
                  'is_upvoted')
        read_only_fields = ('id',)


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""
    user = serializers.SerializerMethodField('get_user')
    question = serializers.SerializerMethodField('get_question')
    comments = serializers.SerializerMethodField('get_comments')
    is_upvoted = serializers.SerializerMethodField('get_is_upvoted')

    def get_comments(self, obj):
        """Returning associated comments"""
        return MinCommentSerializer(Comment.objects.filter(answer=obj).all(), many=True).data

    def get_user(self, obj):
        """Returning the related user"""
        return UserSerializer(obj.user).data

    def get_question(self, obj):
        """Returning the related question"""
        return MinQuestionSerializer(obj.question).data

    def get_is_upvoted(self, obj):
        """Return if the current user has upvoted"""
        user = self.context['request'].user
        upvote_query = obj.upvotes.filter(user=user)
        if not upvote_query.exists():
            obj.upvotes.add(Upvote.objects.create(user=user, answer=obj, has_upvoted=False))
        return obj.upvotes.filter(user=user).first().has_upvoted

    class Meta:
        model = Answer
        fields = ('id', 'text', 'created_at', 'user', 'question', 'comments', 'is_upvoted', 'upvotes_count')
        read_only_fields = ('id',)


class MinCommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = serializers.SerializerMethodField('get_user')

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_at', 'user')
        read_only_fields = ('id',)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = serializers.SerializerMethodField('get_user')
    answer = serializers.SerializerMethodField('get_answer')

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_answer(self, obj):
        return MinAnswerSerializer(obj.answer).data

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_at', 'user', 'answer')
        read_only_fields = ('id', 'user')


class UpvoteSerializer(serializers.ModelSerializer):
    """Serializer for Upvote model"""

    class Meta:
        model = Upvote
        fields = ('id', 'answer', 'question', 'has_upvoted')
        read_only_fields = ('id', 'answer', 'question')
        extra_kwargs = {
            'answer': {'required': False},
            'question': {'required': False},
        }


class PairSessionSerializer(serializers.ModelSerializer):
    """Serializer for Paired Session"""
    mentor = serializers.SerializerMethodField('get_mentor')
    student = serializers.SerializerMethodField('get_student')

    def get_student(self, obj):
        """Return the related student user"""
        return UserSerializer(obj.student.user).data

    def get_mentor(self, obj):
        """Return the related mentor user"""
        return UserSerializer(obj.mentor.user).data

    class Meta:
        model = PairSession
        fields = ("id", "price", "url", "created_at", "mentor",
                  "student", "feedback_session")
        read_only_fields = ("id",)
        extra_kwargs = ("feedback_session",)


class FeedbackFormSerializer(serializers.ModelSerializer):
    """Serializer for feedback form"""

    class Meta:
        model = FeedbackForm
        fields = ("id", "student_satisfied_rating", "mentor_satisfied_rating",
                  "has_student_reported", "has_mentor_reported", "student_comment",
                  "mentor_comment")
        read_only_fields = ("id",)


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ("id", "student", "mentor", "url",
                  "status", "start_datetime", "end_datetime",
                  "created_at", "price", "feedback_form")
        read_only_fields = ("id",)
        extra_kwargs = {
            "feedback_form": {"required": False},
            "url": {"required": False},
            "student": {"required": False}

        }
