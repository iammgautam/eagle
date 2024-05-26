from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CaseHistoryViewSet, HighCourtViewsets

# router = DefaultRouter()
# router.register(r'casehistories', CaseHistoryViewSet)
# router.register(r'high_courts', HighCourtViewsets)
# app_name = 'case_history'
# urlpatterns = [
#     path('', include(router.urls)),
# ]