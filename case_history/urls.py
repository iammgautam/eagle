from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseHistoryViewSet

router = DefaultRouter()
router.register(r'casehistories', CaseHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]