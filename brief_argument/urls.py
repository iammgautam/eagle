from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArgumentViewSet,
    BriefArgumentViewSet,
    main_page,
    step_1,
    step_2,
    admin_home_page,
)
from case_history.views import CaseHistoryViewSet, HighCourtViewsets

router = DefaultRouter()
router.register(r"arguments", ArgumentViewSet)
router.register(r"brief_arguments", BriefArgumentViewSet)
router.register(r"casehistories", CaseHistoryViewSet)
router.register(r"high_courts", HighCourtViewsets)
app_name = "brief_argument"

urlpatterns = [
    path("api/", include(router.urls)),
    path("", main_page, name="home"),
    path("step_1/<uuid:case_id>/", step_1, name="step_1"),
    path("step_2/<uuid:brief_id>/", step_2, name="step_2"),
    path("amsexyniknowit/", admin_home_page, name="admin_home_page"),
]
