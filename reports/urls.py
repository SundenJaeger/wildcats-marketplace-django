from django.urls import path
from . import views

urlpatterns = [
    path('api/reports/', views.report_list, name='report-list'),
    path('api/reports/<int:report_id>/status', views.report_status_update, name='report-status-update'),
    path('api/reports/<int:report_id>/', views.report_delete, name='report-delete'),
]