from django.urls import path
from . import views


urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
     path("api/payment-status/<str:project_name>/", views.payment_status, name="payment_status"),

]
