
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'user', views.UserDetailViewSet, basename='user')
router.register(r"question", views.QuestionDetailViewSet, basename="question")
router.register(r"answer", views.AnswerDetailViewSet, basename="answer")
router.register(r"comment", views.CommentDetailViewSet, basename="comment")
router.register(r"upvote", views.UpvotesViewSet, basename="upvote")
router.register(r"session", views.PairSessionViewSet, basename="session")
router.register(r"feedback", views.FeedbackFormViewSet, basename="feedback")
router.register(r"appointment", views.AppointmentViewSet, basename="appointment")

app_name = "core"

urlpatterns = [
    path('token/', views.ObtainAuthToken.as_view(), name='auth-token'),
    path("core/", include(router.urls)),
]

