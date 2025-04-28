# plaid_integration/views.py
import json
import plaid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .plaid_config import get_plaid_client

def link_token_create(request):
    client = get_plaid_client()
    
    # Create a link_token for the given user
    request_data = {
        'user': {
            'client_user_id': str(request.user.id),  # Use your user's ID
        },
        'client_name': 'Your App Name',
        'products': ['auth', 'transactions'],  # Specify products you need
        'country_codes': ['US'],
        'language': 'en'
    }
    
    try:
        response = client.link_token_create(request_data)
        return JsonResponse(response.to_dict())
    except plaid.ApiException as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
@require_POST
def exchange_public_token(request):
    """Exchange public token for access token and item ID"""
    client = get_plaid_client()
    public_token = json.loads(request.body)['public_token']
    
    try:
        request_data = {
            'public_token': public_token
        }
        
        exchange_response = client.item_public_token_exchange(request_data)
        
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        
        
        return JsonResponse({'success': True})
    except plaid.ApiException as e:
        return JsonResponse({'error': str(e)})

def plaid_link_view(request):
    """Render the template containing Plaid Link"""
    return render(request, 'plaid_integration/link.html')