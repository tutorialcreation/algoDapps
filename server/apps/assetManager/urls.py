
from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from apps.assetManager.views import AssetViewSet

router = DefaultRouter()
router.register("assets", AssetViewSet, basename="assets")
asset_urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/getClient/",AssetViewSet.as_view({'post':'get_algod_client_details'})),
    path("api/v1/genNft/",AssetViewSet.as_view({'post':'gen_nft'})),
    path("api/v1/genApp/",AssetViewSet.as_view({'post':'gen_app'})),
    path("api/v1/donateAsset/",AssetViewSet.as_view({'post':'donate_assets'})),
    path("api/v1/requestAsset/",AssetViewSet.as_view({'post':'request_asset'})),
    path("api/v1/optIn/",AssetViewSet.as_view({'post':'optIn'})),
    path("api/v1/acceptRequest/",AssetViewSet.as_view({'post':'accept_request'})),
    path("api/v1/getAssetParams/",AssetViewSet.as_view({'post':'get_created_asset'})),
    # path("api/v1/getAssetParams/",AssetViewSet.as_view({'post':'get_created_asset'})),
]