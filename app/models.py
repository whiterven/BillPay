from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    plaid_access_token = db.Column(db.String(255), nullable=True)
    plaid_item_id = db.Column(db.String(255), nullable=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    accounts = db.relationship('Account', backref='user', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, nullable=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account_id = db.Column(db.String(255), nullable=False)  # Bank Account ID

class ScheduledPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payee = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    next_payment_date = db.Column(db.DateTime, nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    account_id = db.Column(db.String(255), nullable=False)  # Bank Account ID
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'completed', 'failed'
