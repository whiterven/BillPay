from flask import Flask
from config import Config
from app.plaid_client import create_plaid_client  # Import the create_plaid_client function

app = Flask(__name__)
app.config.from_object(Config)
plaid_client = create_plaid_client()

# Example route to test Plaid client
@app.route('/plaid_test')
def plaid_test():
    response = plaid_client.Item.public_token.create('sandbox_institution', ['auth'])
    return response

if __name__ == "__main__":
    app.run(debug=True)
