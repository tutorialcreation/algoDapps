
from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from apps.roles.views import RoleViewSet

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="roles")
roles_urlpatterns = [path("api/v1/", include(router.urls))]