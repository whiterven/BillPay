import os
from plaid import Client

def create_plaid_client():
    client = Client(
        client_id=os.environ.get('PLAID_CLIENT_ID'),
        secret=os.environ.get('PLAID_SECRET'),
        environment=os.environ.get('PLAID_ENV'),
    )
    return client
