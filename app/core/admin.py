from django.contrib import admin

from . import models
import requests


class DegreeAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super(DegreeAdmin, self).save_model(
            request, obj, form, change
        )
        if not change:
            response = requests.get(
                f'http://api.datamuse.com/words?ml={obj.name.lower()}&topics=education,career&max=1000')

            keywords = []
            for word in response.json():
                word_text = word['word']
                keywords.append(models.Keyword(
                    name=word_text,
                    degree=obj
                ))

            models.Keyword.objects.bulk_create(keywords)


admin.site.register(models.Keyword)
admin.site.register(models.Degree, DegreeAdmin)
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
admin.site.register(models.Appointment)
admin.site.register(models.Notification)
