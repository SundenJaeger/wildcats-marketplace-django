from django.urls import path
from . import views

urlpatterns = [
    path('', views.categories_list, name='categories'),
    path('<int:category_id>/', views.category_detail, name='category_detail')
]
