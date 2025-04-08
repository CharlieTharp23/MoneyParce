# plaid_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create_link_token/', views.link_token_create, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
    path('link/', views.plaid_link_view, name='plaid_link'),
]