from django.urls import path
from . import views

urlpatterns = [
    path('', views.verification_requests_list, name='verification_requests_list'),
    path('<int:verification_id>/', views.verification_request_detail, name='verification_request_detail'),
    path('<int:verification_id>/status', views.verification_request_detail, name='verification_request_status_update'),
]
