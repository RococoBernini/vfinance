from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, abort, make_response
from flask_login import current_user

from vfinance.forms import QuoteForm
from vfinance.models import TradeHistory, Portfolio, User
from vfinance.utils import lookup
from vfinance.extensions import db
home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    
    if current_user.is_authenticated:
        form = QuoteForm()
    
        if form.validate_on_submit():
            
            symbol = form.symbol.data
                            
            return redirect(url_for('admin.show_quote', symbol = symbol))    
            
            
        # stocks = Portfolio.query.filter_by(symbol = "AMZN")
        # stocks = Portfolio.query.with_parent(current_user).all()
        # y = []
        # for stock in stocks:
            
        #     flash(stock.symbol)
        #     quote = lookup(stock.symbol)
        #     price = quote['name']
        #     y.append(stock.symbol)
        cash = current_user.cash
        page = request.args.get('page',1,type=int)
        per_page = 15
        pagination = Portfolio.query.with_parent(current_user).order_by(Portfolio.name.asc()).paginate(page,per_page)
        portfolio = pagination.items
        prices = []
        position = 0
        if portfolio:
            for stock in portfolio:
                
                quote = lookup(stock.symbol)
                quantity = stock.quantity
                price = quote['price']
                prices.append(price) 
                position += float(quantity)*float(price)
        
        current_user.position = position       
        account_value = float(cash) + float(position)
        db.session.commit()
        return render_template("home/index.html", portfolio= portfolio, pagination = pagination, prices = prices, cash = cash, position = position, account_value = account_value, form = form)
    else:
        return render_template("home/index.html")