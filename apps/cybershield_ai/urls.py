from django.urls import path

from . import views

app_name = 'cybershield'

urlpatterns = [
    path('', views.home, name='home'),
    path('phishing/', views.phishing, name='phishing'),
    path('deepfake/', views.deepfake, name='deepfake'),
    path('trainer/', views.trainer, name='trainer'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
