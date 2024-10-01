from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from gondorapi.views import UserViewSet

router = routers.DefaultRouter(trailing_slash=False)

urlpatterns = [
    path('', include(router.urls)),
    path("register", UserViewSet.as_view({"post": "register_account"}), name="register")
]

