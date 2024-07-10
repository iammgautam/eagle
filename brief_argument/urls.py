from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    main_page,
    step_1,
    step_2,
    step_3,
    admin_home_page,
    aib_exam,
    aib_step_1,
    aib_step_2,
    aib_exam_adim_page,
    legal_memo_frontend,
    legal_search,
)
from .viewsets import (
    ArgumentViewSet,
    AIBExammViewsets,
    LegalMemorandumViewsets,
    HulsburyLawBooksViewsets,
    StatementEmbeddingsViewsets,
    RelevantCitationsPassageViewsets,
    CaseViewsets
)
from case_history.views import CaseHistoryViewSet, HighCourtViewsets, LegalSearchHistoryViewsets

router = DefaultRouter()
router.register(r"arguments", ArgumentViewSet)
router.register(r"legal_memo", LegalMemorandumViewsets)
router.register(r"aib_exam", AIBExammViewsets)
router.register(r"casehistories", CaseHistoryViewSet)
router.register(r"high_courts", HighCourtViewsets)
router.register(r"law_books", HulsburyLawBooksViewsets)
router.register(r"statement", StatementEmbeddingsViewsets)
router.register(r"relevant_citations", RelevantCitationsPassageViewsets)
router.register(r"legal_search", LegalSearchHistoryViewsets)
router.register(r"lexplore", CaseViewsets)
app_name = "brief_argument"

urlpatterns = [
    path("api/", include(router.urls)),
    path("", main_page, name="home"),
    path("step_1/<uuid:case_id>/", step_1, name="step_1"),
    path("step_2/<uuid:legal_memo_id>/", step_2, name="step_2"),
    path("step_3/<uuid:legal_memo_id>/", step_3, name="step_3"),
    path("amsexyniknowit/", admin_home_page, name="admin_home_page"),
    path("aib/", aib_exam, name="aib_exam"),
    path("step_1/<int:aib_exam_id>/", aib_step_1, name="aib_step_1"),
    path("step_2/<int:aib_exam_id>/", aib_step_2, name="aib_step_2"),
    path("aib_admin/", aib_exam_adim_page, name="aib_exam_admin_page"),
    path("search/", legal_search, name="legal_search"),
    path(
        "legal_memorandum/<uuid:legal_memo_id>/",
        legal_memo_frontend,
        name="legal_memo_fe",
    ),
]
