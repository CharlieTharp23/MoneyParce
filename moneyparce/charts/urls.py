from django.urls import path
from . import views

""" urlpatterns = [
    path('charts/', views.chart_view, name='chart'),
] """

urlpatterns = [
    path('', views.test_chart_view, name='chart'),
]
