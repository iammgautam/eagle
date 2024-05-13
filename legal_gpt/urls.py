from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/brief_arguments/", include("brief_argument.urls")),
    path("api/case_history/", include("case_history.urls")),
]
