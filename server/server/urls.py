from django.contrib import admin
from django.urls import path

from apps.accounts.urls import accounts_urlpatterns
from apps.notes.urls import notes_urlpatterns
from apps.roles.urls import roles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += accounts_urlpatterns # add URLs for authentication
urlpatterns += notes_urlpatterns # notes URLs
urlpatterns += roles_urlpatterns # roles URLs