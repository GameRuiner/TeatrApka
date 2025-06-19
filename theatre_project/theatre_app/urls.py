from django.urls import path
from . import views

app_name = 'theatre_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('performance/<int:performance_id>/', views.performance_detail, name='performance_detail'),
    path('api/performances/', views.api_performances, name='api_performances'),
]