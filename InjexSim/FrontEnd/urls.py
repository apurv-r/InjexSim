from django.urls import path
from . import views

app_name = 'FrontEnd'

urlpatterns = [
    path('', views.home, name='home'),
    path('loginPage/', views.loginPage, name='loginPage'),
    path('itemSearch/', views.itemSearch, name='itemSearch'),
    path('database/', views.database, name='database'),
    path('mitigate/', views.mitigate, name='mitigate'),
]