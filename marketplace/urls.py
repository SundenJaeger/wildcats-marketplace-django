from django.urls import path
from . import views
from .views import CommentsByResourceView, AddCommentView
from .views import (
    HomePageView,
    CreateResourceView,
    UploadResourceImagesView,
    AvailableResourcesView
)

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('resources/', CreateResourceView.as_view(), name='create_resource'),
    path('resources/available/', AvailableResourcesView.as_view(), name='available_resources'),
    path('resources/<int:resource_id>/images/', UploadResourceImagesView.as_view(), name='upload_resource_images'),
    path('api/comments/resource/<int:resource_id>/', CommentsByResourceView.as_view()),
    path('api/comments/<int:student_id>/', AddCommentView.as_view()),
]