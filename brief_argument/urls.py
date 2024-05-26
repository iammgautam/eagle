from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArgumentViewSet, BriefArgumentViewSet, main_page, research_input, counsel_input, admin_home_page
from case_history.views import CaseHistoryViewSet, HighCourtViewsets
router = DefaultRouter()
router.register(r'arguments', ArgumentViewSet)
router.register(r'brief_arguments', BriefArgumentViewSet)
router.register(r'casehistories', CaseHistoryViewSet)
router.register(r'high_courts', HighCourtViewsets)
app_name = 'brief_argument'

urlpatterns = [
    path('api/', include(router.urls)),
    path('', main_page, name="home"),
    path('research_input/<uuid:case_id>/', research_input, name='research_input'),
    path('counsel_input/<uuid:brief_id>/', counsel_input, name='counsel_input'),
    path('amsexyniknowit/', admin_home_page, name='admin_home_page'),

]
