from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.create_transaction, name='create_transaction'),
    path('', views.transaction_list, name='transaction_list')
]