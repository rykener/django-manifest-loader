from django.urls import path
from django_project.frontend import views

urlpatterns = [
    path('', views.home),
]
