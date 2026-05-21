from django.urls import path
from . import views

app_name = 'cybershield'

urlpatterns = [
    path('', views.home, name='home'),
    path('phishing/', views.phishing, name='phishing'),
    path('deepfake/', views.deepfake, name='deepfake'),
    path('trainer/', views.trainer, name='trainer'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forum/', views.forum, name='forum'),
    path('forum/new/', views.forum_create, name='forum_create'),
    path('forum/<int:post_id>/', views.forum_detail, name='forum_detail'),
    path('forum/<int:post_id>/comment/', views.forum_comment, name='forum_comment'),
    path('forum/<int:post_id>/like/', views.forum_like, name='forum_like'),
    path('profile/', views.profile, name='profile'),
    path('users/<str:username>/', views.public_profile, name='public_profile'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_confirm, name='logout'),
    path('language/<str:language>/', views.set_language, name='set_language'),
]
