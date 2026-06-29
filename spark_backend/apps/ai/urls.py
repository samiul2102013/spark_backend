from django.urls import path

from . import views

urlpatterns = [
    path(
        "ai/control-config/",
        views.message_review_config_view,
        name="ai-message-review-config",
    ),
    path(
        "ai/reporting-config/",
        views.ai_reporting_config_view,
        name="ai-reporting-config",
    ),
    path(
        "ai/message-review/",
        views.message_review_list_view,
        name="ai-message-review-list",
    ),
    path(
        "ai/message-review/<str:source>/<int:item_id>/",
        views.message_review_detail_view,
        name="ai-message-review-detail",
    ),
    path(
        "ai/reports/",
        views.situation_report_list_view,
        name="ai-report-list",
    ),
    path(
        "ai/reports/<int:report_id>/",
        views.situation_report_detail_view,
        name="ai-report-detail",
    ),
]
