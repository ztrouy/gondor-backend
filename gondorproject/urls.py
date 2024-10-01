from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from gondorapi.views import AuthViewSet

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('', include(router.urls)),
    path("register", AuthViewSet.as_view({"post": "register_patient"}), name="register"),
    path("login", AuthViewSet.as_view({"post": "login"}), name="login")
]

