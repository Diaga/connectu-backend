from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    BaseUserManager
from django.utils import timezone
from uuid import uuid4


class Keyword(models.Model):

    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'core'
        default_related_name = 'keywords'

    def __str__(self):
        return self.name


class Degree(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'core'
        default_related_name = 'degrees'

    def __str__(self):
        return self.name


class University(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    degrees = models.ManyToManyField(Degree)

    class Meta:
        app_label = 'core'
        default_related_name = 'universities'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):

    def create_user(self, email, password, **kwargs):
        if not email or not password:
            raise ValueError('Please specify email and password!')

        user = self.model(email=email.lower(), **kwargs)
        user.set_password(password)

        user.save()

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True

        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    is_staff = models.BooleanField(default=False)

    keywords = models.ManyToManyField('Keyword')
    mentor = models.OneToOneField('Mentor', on_delete=models.CASCADE)
    student = models.OneToOneField('Student', on_delete=models.CASCADE)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @property
    def is_mentor(self):
        return self.mentor is not None

    class Meta:
        app_label = 'core'

    def __str__(self):
        return self.email


class Mentor(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    is_professional = models.BooleanField(default=False)
    points = models.PositiveIntegerField(default=0)

    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    class Meta:
        app_label = 'core'
        default_related_name = 'mentors'

    def __str__(self):
        return f'{self.user.email} Mentor'


class Student(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    class Meta:
        app_label = 'core'
        default_related_name = 'students'

    def __str__(self):
        return f'{self.user.email} Student'


class Question(models.Model):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)

    title = models.CharField(max_length=255)
    text = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keywords = models.ForeignKey(Keyword, on_delete=models.CASCADE)

    @property
    def upvotes_count(self):
        return self.upvotes.count()

    class Meta:
        app_label = 'core'
        default_related_name = 'questions'

    def __str__(self):
        return f'{self.title} by {self.user.email}'


class Answer(models.Model):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)

    text = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    @property
    def upvotes_count(self):
        return self.upvotes.count()

    class Meta:
        app_label = 'core'
        default_related_name = 'answers'

    def __str__(self):
        return f'{self.text} by {self.user.email}'


class Comment(models.Model):

    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    text = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        app_label = 'core'
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.text} by {self.user.email}'


class Upvote(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    has_upvoted = models.BooleanField(default=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = 'core'
        default_related_name = 'upvotes'

    def __str__(self):
        return f'Upvote by {self.user.email}'


class FeedbackForm(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    student_satisfied_rating = models.PositiveSmallIntegerField(null=True)
    mentor_satisfied_rating = models.PositiveSmallIntegerField(null=True)

    has_student_reported = models.BooleanField(default=False)
    has_mentor_reported = models.BooleanField(default=False)

    student_comment = models.TextField(blank=True)
    mentor_comment = models.TextField(blank=True)

    class Meta:
        app_label = 'core'
        default_related_name = 'feedback_forms'

    def __str__(self):
        return f'Feedback form of {self.pair_session}'


class PairSession(models.Model):

    id = models.UUIDField(editable=False, default=uuid4, primary_key=True)

    price = models.FloatField(default=0)
    url = models.CharField(max_length=255)

    created_at = models.DateTimeField(default=timezone.now)

    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    feedback_session = models.OneToOneField(FeedbackForm, on_delete=models.CASCADE)

    class Meta:
        app_label = 'core'
        default_related_name = 'pair_sessions'

    def __str__(self):
        return f'{self.mentor.user.email} paired with {self.student.user.email}'
