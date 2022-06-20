from django.contrib import admin
from django.urls import path

from apps.accounts.urls import accounts_urlpatterns
from apps.notes.urls import notes_urlpatterns
from apps.assetManager.urls import asset_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += accounts_urlpatterns # add URLs for authentication
urlpatterns += notes_urlpatterns # notes URLs
urlpatterns += asset_urlpatterns # roles URLs