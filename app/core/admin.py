from django.contrib import admin

from . import models

admin.site.register(models.Keyword)
admin.site.register(models.Degree)
admin.site.register(models.University)
admin.site.register(models.User)
admin.site.register(models.Mentor)
admin.site.register(models.Student)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.Comment)
admin.site.register(models.Upvote)
admin.site.register(models.FeedbackForm)
admin.site.register(models.PairSession)
