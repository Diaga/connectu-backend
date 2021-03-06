# Generated by Django 2.2.16 on 2020-12-06 15:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'default_related_name': 'answers',
            },
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'default_related_name': 'degrees',
            },
        ),
        migrations.CreateModel(
            name='FeedbackForm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_satisfied_rating', models.PositiveSmallIntegerField(null=True)),
                ('mentor_satisfied_rating', models.PositiveSmallIntegerField(null=True)),
                ('has_student_reported', models.BooleanField(default=False)),
                ('has_mentor_reported', models.BooleanField(default=False)),
                ('student_comment', models.TextField(blank=True)),
                ('mentor_comment', models.TextField(blank=True)),
            ],
            options={
                'default_related_name': 'feedback_forms',
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'default_related_name': 'keywords',
            },
        ),
        migrations.CreateModel(
            name='Mentor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_professional', models.BooleanField(default=False)),
                ('points', models.PositiveIntegerField(default=0)),
                ('degree', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentors', to='core.Degree')),
            ],
            options={
                'default_related_name': 'mentors',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('keywords', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='core.Keyword')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'questions',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'default_related_name': 'students',
            },
        ),
        migrations.CreateModel(
            name='Upvote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('has_upvoted', models.BooleanField(default=False)),
                ('answer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to='core.Answer')),
                ('question', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to='core.Question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='upvotes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'upvotes',
            },
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('degrees', models.ManyToManyField(related_name='universities', to='core.Degree')),
            ],
            options={
                'default_related_name': 'universities',
            },
        ),
        migrations.CreateModel(
            name='PairSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('price', models.FloatField(default=0)),
                ('url', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('feedback_session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pair_sessions', to='core.FeedbackForm')),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pair_sessions', to='core.Mentor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pair_sessions', to='core.Student')),
            ],
            options={
                'default_related_name': 'pair_sessions',
            },
        ),
        migrations.AddField(
            model_name='mentor',
            name='university',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentors', to='core.University'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.Answer')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_related_name': 'comments',
            },
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='core.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='keywords',
            field=models.ManyToManyField(to='core.Keyword'),
        ),
        migrations.AddField(
            model_name='user',
            name='mentor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Mentor'),
        ),
        migrations.AddField(
            model_name='user',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Student'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
