from django.contrib import admin

from . import models

admin.register(models.Keyword)
admin.register(models.Degree)
admin.register(models.University)
admin.register(models.User)
admin.register(models.Mentor)
admin.register(models.Student)
admin.register(models.Question)
admin.register(models.Answer)
admin.register(models.Comment)
admin.register(models.Upvote)
admin.register(models.FeedbackForm)
admin.register(models.PairSession)
