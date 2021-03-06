
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'university', views.UniversityViewSet, basename='university')
router.register(r'degree', views.DegreeDetailViewSet, basename='degree')
router.register(r'user', views.UserDetailViewSet, basename='user')
router.register(r'question', views.QuestionDetailViewSet, basename='question')
router.register(r'answer', views.AnswerDetailViewSet, basename='answer')
router.register(r'comment', views.CommentDetailViewSet, basename='comment')
router.register(r'upvote', views.UpvotesViewSet, basename='upvote')
router.register(r'session', views.PairSessionViewSet, basename='session')
router.register(r'feedback', views.FeedbackFormViewSet, basename='feedback')
router.register(r'appointment', views.AppointmentViewSet, basename='appointment')
router.register(r'about_me', views.AboutMeViewSet, basename='about_me')
router.register(r'mentor_pair', views.MentorPairStudentViewSet, basename='mentor_pair')
router.register(r'notification', views.NotificationViewSet, basename='notification')

app_name = 'core'

urlpatterns = [
    path('token/', views.AuthTokenViewSet.as_view(), name='auth-token'),
    path('core/', include(router.urls)),
]
