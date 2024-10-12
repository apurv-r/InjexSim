from django.urls import path
from . import views

app_name = 'FrontEnd'

urlpatterns = [
    path('', views.home, name='home'),
    path('database/', views.database, name='database'),
]