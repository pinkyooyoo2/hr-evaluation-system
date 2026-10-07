from django.urls import path

from evaluations.views import (
    admin_response_status_view,
    admin_result_csv_view,
    admin_result_summary_view,
    employee_score_view,
    evaluation_item_detail,
    evaluation_item_list_create,
    evaluation_response_detail,
    evaluation_response_list_create,
)

urlpatterns = [
    path('evaluation-items/', evaluation_item_list_create, name='evaluation-item-list-create'),
    path('evaluation-items/<int:pk>/', evaluation_item_detail, name='evaluation-item-detail'),
    path('evaluations/responses/', evaluation_response_list_create, name='evaluation-response-list-create'),
    path('evaluations/responses/<int:pk>/', evaluation_response_detail, name='evaluation-response-detail'),
    path('evaluations/my-score/', employee_score_view, name='employee-score'),
    path('evaluations/status/', admin_response_status_view, name='admin-response-status'),
    path('evaluations/results/summary/', admin_result_summary_view, name='admin-result-summary'),
    path('evaluations/results/csv/', admin_result_csv_view, name='admin-result-csv'),
]
