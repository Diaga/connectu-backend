from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    BaseUserManager
from django.utils import timezone
from uuid import uuid4


class Keyword(models.Model):

    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=255)
    degree = models.ForeignKey('Degree', on_delete=models.CASCADE)

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

    keywords = models.ManyToManyField('Keyword', blank=True)
    mentor = models.OneToOneField('Mentor', on_delete=models.CASCADE, null=True, blank=True)
    student = models.OneToOneField('Student', on_delete=models.CASCADE, null=True, blank=True)

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

    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, null=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = 'core'
        default_related_name = 'mentors'

    def __str__(self):
        return f'{self.user.email} Mentor'


class Student(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    degree1 = models.ForeignKey(Degree, related_name='degree1', on_delete=models.SET_NULL, null=True)
    degree2 = models.ForeignKey(Degree, related_name='degree2', on_delete=models.SET_NULL, null=True)
    degree3 = models.ForeignKey(Degree, related_name='degree3', on_delete=models.SET_NULL, null=True)

    class Meta:
        app_label = 'core'
        default_related_name = 'students'


class Question(models.Model):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)

    title = models.CharField(max_length=255)
    text = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(Keyword)

    @property
    def upvotes_count(self):
        return self.upvotes.filter(has_upvoted=True).count()

    class Meta:
        app_label = 'core'
        default_related_name = 'questions'

    def __str__(self):
        return f'{self.title} by {self.user.email}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Create Upvote objects after creating new Question"""
        super(Question, self).save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )

        if len(self.upvotes.all()) == 0:

            for user in User.objects.all():
                Upvote.objects.get_or_create(
                    question=self,
                    user=user,
                    answer=None
                )

        else:
            raise AssertionError


class Answer(models.Model):

    id = models.UUIDField(editable=False, primary_key=True, default=uuid4)

    text = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    @property
    def upvotes_count(self):
        return self.upvotes.filter(has_upvoted=True).count()

    class Meta:
        app_label = 'core'
        default_related_name = 'answers'

    def __str__(self):
        return f'{self.text} by {self.user.email}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Create Upvote objects after creating new Answer"""
        super(Answer, self).save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )

        if len(self.upvotes.all()) == 0:

            for user in User.objects.all():
                Upvote.objects.get_or_create(
                    answer=self,
                    user=user,
                    question=None
                )

        else:
            raise AssertionError


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

    # def __str__(self):
    #     return f'Feedback form of {self.pair_sessions}'


class PairSession(models.Model):

    id = models.UUIDField(editable=False, default=uuid4, primary_key=True)

    price = models.FloatField(default=0)
    url = models.CharField(max_length=255)

    created_at = models.DateTimeField(default=timezone.now)

    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    feedback_session = models.OneToOneField(FeedbackForm, on_delete=models.CASCADE,
                                            null=True, blank=True)

    class Meta:
        app_label = 'core'
        default_related_name = 'pair_sessions'

    def __str__(self):
        return f'{self.mentor.user.email} paired with {self.student.user.email}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Create feedback form objects after creating new PairSession"""
        if self.feedback_session is None:
            self.feedback_session = FeedbackForm.objects.create()
            Notification.objects.create(
                user=self.mentor.user,
                title=f'Mentoring session request by {self.student.user.name} at {self.url}',
                feedback_form=self.feedback_session
            )
        else:
            return AssertionError
        super(PairSession, self).save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields
        )


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    url = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField(default=0)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    price = models.FloatField(default=0)

    feedback_form = models.OneToOneField(FeedbackForm, on_delete=models.CASCADE,
                                         null=True, blank=True)

    class Meta:
        app_label = 'core'
        default_related_name = 'appointments'

    def __str__(self):
        return f'{self.mentor.user.email} paired with {self.student.user.email}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Create feedback form objects after creating new Appointment"""
        if self.feedback_form is None:
            self.feedback_form = FeedbackForm.objects.create()
            super(Appointment, self).save(
                    force_insert=force_insert, force_update=force_update, using=using,
                    update_fields=update_fields
                )
        else:
            super(Appointment, self).save(
                force_insert=force_insert, force_update=force_update, using=using,
                update_fields=update_fields
            )
            return AssertionError


class Notification(models.Model):
    id = models.UUIDField(default=uuid4, editable=False, primary_key=True)

    feedback_form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255,null=True, blank=True)
    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'core'
        default_related_name = 'notifications'

    def __str__(self):
        return f'{self.title} for {self.user.name}'
