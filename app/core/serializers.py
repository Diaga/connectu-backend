from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import User, Mentor, Student, Degree, University


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
        fields = ('id', 'is_professional', 'points', 'degree', 'university')
        read_only_fields = ('id', 'points', )

    def create(self, validated_data):

        degree = validated_data.pop('degree', None)
        university = validated_data.pop('university', None)

        mentor = super(MentorSerializer, self).create(validated_data)

        if degree is not None:
            mentor.degree = Degree.objects.get(pk=degree)

        if university is not None:
            mentor.university = University.objects.get(pk=university)

        mentor.save()

        return mentor

    def update(self, instance, validated_data):

        degree = validated_data.pop('degree', None)
        university = validated_data.pop('university', None)

        mentor = super(MentorSerializer, self).update(instance, validated_data)

        if degree is not None:
            mentor.degree = Degree.objects.get(pk=degree)

        if university is not None:
            mentor.university = University.objects.get(pk=university)

        mentor.save()

        return mentor


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ('id', )
        read_only_fields = ('id', )


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
        read_only_fields = ('id', )

    def create(self, validated_data):

        mentor = validated_data.pop('mentor', None)
        student = validated_data.pop('student', None)

        if mentor is not None and student is not None:
            raise ValueError('A user cannot be both mentor and student!')

        user = User.objects.create_user(**validated_data)

        if mentor is not None:
            user.mentor = Mentor.objects.create(**mentor)
        elif student is not None:
            user.student = Student.objects.create(**student)

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
