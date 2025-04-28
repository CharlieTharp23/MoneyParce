# plaid_integration/plaid_config.py
import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api

# Load environment variables from .env file
load_dotenv()

# Get environment variables
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID')
PLAID_SECRET = os.environ.get('PLAID_SECRET')
PLAID_ENVIRONMENT = os.environ.get('PLAID_ENVIRONMENT', 'sandbox')

def get_plaid_client():
    # Map environment string to Plaid environment
    environment_map = {
        'sandbox': plaid.Environment.Sandbox,
        'development': plaid.Environment.Development,
        'production': plaid.Environment.Production
    }
    
    plaid_env = environment_map.get(PLAID_ENVIRONMENT, plaid.Environment.Sandbox)
    
    # Configure the Plaid client
    configuration = plaid.Configuration(
        host=plaid_env,
        api_key={
            'clientId': PLAID_CLIENT_ID,
            'secret': PLAID_SECRET,
        }
    )
    
    # Create API client
    api_client = plaid.ApiClient(configuration)
    client = plaid_api.PlaidApi(api_client)
    
    return client