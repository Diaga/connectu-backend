
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"question", views.QuestionDetailViewSet, basename="question")

app_name = "core"

urlpatterns = [
    path('token/', views.ObtainAuthToken.as_view(), name='auth-token'),
    path("core/", include(router.urls)),
]

