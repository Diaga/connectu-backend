from django.urls import path

from . import views

urlpatterns = [
    path('token/', views.ObtainAuthToken.as_view(), name='auth-token')
]
