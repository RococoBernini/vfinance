from vfinance.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True)
    password_hash = db.Column(db.String(128))
    cash = db.Column(db.Numeric(10,2))
    position = db.Column(db.Numeric(10,2))
    trade_history = db.relationship("TradeHistory", back_populates='user', cascade='all, delete-orphan')
    portfolio = db.relationship("Portfolio", back_populates = 'user', cascade='all, delete-orphan')
    watchlist = db.relationship("Watchlist", back_populates = 'user', cascade='all, delete-orphan')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class TradeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    symbol = db.Column(db.String(10))
    name = db.Column(db.String(50)) 
    price = db.Column(db.Numeric(10,2))
    action = db.Column(db.String(10))
    quantity = db.Column(db.Numeric(10,2))
   

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates = 'trade_history')

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    symbol = db.Column(db.String(10))
    name = db.Column(db.String(50))
    purchase_price = db.Column(db.Numeric(10,2))
    quantity = db.Column(db.Numeric(10,2))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates = 'portfolio')


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    symbol = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates = 'watchlist')

  