from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('categories/', views.CategoryList.as_view(), name='categories'),
    path('categories/create/', views.CreateCategory.as_view(), name='create_category'),
    path('post-advertise/', views.CreateAd.as_view(), name='create_ad'),
    path('car/<pk>/', views.CarDetail.as_view(), name='Car_detail'),
]
