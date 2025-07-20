from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('user_login/', views.user_login, name='user_login'),
    path('doctor-login/', views.doctor_login, name='doctor_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('register/', views.user_register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('get_time_slots/', views.fetch_time_slots, name='get_time_slots'),
    path('logout/', views.user_logout, name='logout'),
]
