
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("question", views.QuestionViewSet)

app_name = "core"

urlpatterns = [
    path('token/', views.ObtainAuthToken.as_view(), name='auth-token'),
    path("", include(router.urls)),
]

