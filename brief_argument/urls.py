from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArgumentViewSet, BriefArgumentViewSet
router = DefaultRouter()
router.register(r'arguments', ArgumentViewSet)
router.register(r'brief_arguments', BriefArgumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
