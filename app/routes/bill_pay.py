from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, ScheduledPayment, Account
import plaid
import os
from datetime import datetime, timedelta

bill_pay = Blueprint('bill_pay', __name__)

plaid_client = plaid.Client(
    client_id=os.getenv('PLAID_CLIENT_ID'),
    secret=os.getenv('PLAID_SECRET'),
    environment=os.getenv('PLAID_ENV')
)

@bill_pay.route('/bill_pay', methods=['GET', 'POST'])
@login_required
def bill_pay_route():
    if request.method == 'POST':
        payee = request.form.get('payee')
        amount = float(request.form.get('amount'))
        payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        frequency = request.form.get('frequency')
        account_id = request.form.get('account_id')

        # Input Validation
        if not payee or not amount or not payment_date or not frequency or not account_id:
            return 'Please fill in all fields', 400

        # Check if user has an active Plaid connection
        if not current_user.plaid_access_token or not current_user.plaid_item_id:
            return 'Please connect your bank account first', 400

        # Determine Next Payment Date
        if frequency == 'daily':
            next_payment_date = payment_date + timedelta(days=1)
        elif frequency == 'weekly':
            next_payment_date = payment_date + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_payment_date = payment_date + timedelta(days=30)  # Approximation for monthly

        # Create Scheduled Payment
        new_payment = ScheduledPayment(
            user_id=current_user.id,
            payee=payee,
            amount=amount,
            next_payment_date=next_payment_date,
            frequency=frequency,
            account_id=account_id
        )
        db.session.add(new_payment)
        db.session.commit()

        # Initiate ACH Payment using Plaid's ACH API
        try:
            ach_response = plaid_client.ACH.create(
                access_token=current_user.plaid_access_token,
                account_id=account_id,
                amount=amount,
                description="Bill Payment",
                iso_currency_code="USD",
                name=payee,
            )

            # Store Payment ID and Status
            new_payment.status = 'completed'  # Or 'pending' depending on Plaid's response
            db.session.commit()

            return 'ACH Payment initiated', 200
        except plaid.errors.PlaidError as e:
            return jsonify({'error': str(e)}), 500

    # Get Available Bank Accounts
    try:
        accounts = plaid_client.Accounts.get(access_token=current_user.plaid_access_token)
        # Update Account Information in Database
        for account in accounts['accounts']:
            existing_account = Account.query.filter_by(user_id=current_user.id, account_id=account['account_id']).first()
            if existing_account:
                existing_account.name = account['name']
                existing_account.account_type = account['type']
                existing_account.balance = account['balances']['current']
            else:
                new_account = Account(
                    user_id=current_user.id,
                    account_id=account['account_id'],
                    name=account['name'],
                    account_type=account['type'],
                    balance=account['balances']['current']
                )
                db.session.add(new_account)
                db.session.commit()

        return render_template('bill_pay.html', accounts=accounts['accounts'])
    except plaid.errors.PlaidError as e:
        return jsonify({'error': str(e)}), 500
