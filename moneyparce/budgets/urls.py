from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('sliders/', views.budget_sliders, name='budget_sliders'),
    path('add/', views.add_budget, name='add_budget'),
    path('edit/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),
]