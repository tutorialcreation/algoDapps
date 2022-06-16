
from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from apps.assetManager.views import AssetViewSet

router = DefaultRouter()
router.register("assets", AssetViewSet, basename="assets")
asset_urlpatterns = [path("api/v1/", include(router.urls))]