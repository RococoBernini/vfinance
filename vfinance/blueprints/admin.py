import os

from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail
from vfinance.utils import lookup, redirect_back
from vfinance.forms import QuoteForm, TradeForm
from vfinance.models import User, TradeHistory, Portfolio, Watchlist
from vfinance.extensions import db
from vfinance.kchart import chart_plot_upload


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/quote', methods=["GET", "POST"])
@login_required
def get_quote():
    form = QuoteForm()
    if form.validate_on_submit():
        symbol = form.symbol.data
        
        quote = lookup(symbol)
        
        if quote:
            
            return redirect(url_for(".show_quote", symbol = symbol))
        else:
            flash("Cannot find", 'warning')
            return redirect_back()
    return render_template("admin/quote.html", form = form)
    

@admin_bp.route('/quote/<string:symbol>', methods =["GET","POST"])
@login_required
def show_quote(symbol):
    form = QuoteForm()
    quote = lookup(symbol)
    company = quote["name"]
    price = quote["price"]
    symbol = quote['symbol']
    
    # link = chart_plot_upload(symbol)
    # if form.validate_on_submit():
    #     symbol = form.symbol.data
    #     quote = lookup(symbol)
    #     company = quote["name"]
    #     price = quote["price"]
    #     return redirect(url_for(".show_quote", symbol = symbol))
    return render_template("admin/show_quote.html",form = form, company = company, price = price, symbol = symbol)


@admin_bp.route("/trade/<string:symbol>", methods=['GET', 'POST'])
@login_required
def get_trade(symbol):
    # symbol = request.args.get("symbol")
    form = TradeForm()
    quote = lookup(symbol)
    if form.validate_on_submit():
        symbol = form.symbol.data
        quantity = form.quantity.data
        price = form.price.data
        action = form.action.data
        return redirect(url_for('.review_order', symbol = symbol, quantity= quantity, price = price, action = action))
    form.symbol.data = symbol
    form.price.data = quote['price']
    return render_template("admin/get_trade.html", form = form)

# @admin_bp.route('/trade/review/<string:symbol>/<int:quantity>/<float:price>', methods=['GET', 'POST'])
# @login_required
# def review_order(symbol, quantity, price):
    
#     return render_template("admin/review_order.html", symbol = symbol, price = price, quantity = quantity)

@admin_bp.route('/trade/review', methods=['GET', 'POST'])
@login_required
def review_order():
    cash = current_user.cash
    symbol = request.args.get('symbol')
    price = request.args.get('price')
    quantity = request.args.get('quantity')
    action = request.args.get('action')
    totalprice = float(price)*float(quantity)
    able_to_trade = True
    stocklist = []
    if action == 'Buy':
        cash_balance = float(cash) - totalprice
        if cash_balance < 0:
            able_to_trade = False
            flash("Your order be rejected if you do not have enough cash to cover this closing transaction.", 'danger')
            return redirect_back()
    else:
        cash_balance = float(cash) + totalprice
        portfolio = Portfolio.query.with_parent(current_user).all()
        # check if any existed portfolio, if no, return direct_back
        if portfolio:
        
            for company in portfolio:    
                stocklist.append(company.symbol)
            
            if symbol in stocklist:
                id = company.id
                stock = Portfolio.query.get_or_404(id)
                own_quantity = float(stock.quantity)
                if float(quantity) > own_quantity:
                    able_to_trade = False
                    flash("Your share isn't enough for the trade. the order was rejected", 'danger')
                    return redirect_back()
            else:
                flash("You dont have any share yet", 'danger')
                return redirect_back()

            #     if symbol in company.symbol:
            #         id = company.id
            #         stock = Portfolio.query.get_or_404(id) 
            #         own_quantity = float(stock.quantity)
            #         if float(quantity) > own_quantity:
            #             able_to_trade = False
            #             flash("Your share isn't enough for the trade. the order was rejected", 'danger')
            #             return redirect_back()
            
            # flash("You dont have any share yet", 'danger')
            # return redirect_back()      
        else:
           able_to_trade = False
           flash("You portfolio is empty", 'danger')
           return redirect_back()
        
    # if cash_balance < 0:
    #     flash("You dont have enough money", 'danger')
    #     return redirect_back()
     
    return render_template("admin/review_order.html",able_to_trade = able_to_trade, action = action, symbol = symbol, price= price, quantity = quantity, cash = cash, totalprice=totalprice, cash_balance=cash_balance)

@admin_bp.route('/trade/placeorder', methods=['GET', 'POST'])
@login_required
def place_order():
    # get trade condition
    able_to_trade = request.args.get('able_to_trade')
    action = request.args.get("action")
    if able_to_trade:
        # get original cash and position
        cash = float(current_user.cash)
        # position = float(current_user.position)
        

        # update cash and position back to database
        if action =="Buy":
            totalprice = float(request.args.get('totalprice'))
            current_user.cash = cash - totalprice
            # current_user.position = position + totalprice
        else:
            totalprice = float(request.args.get('totalprice'))
            current_user.cash = cash + totalprice
            # current_user.position = position - totalprice

        #update trade_history
        symbol = request.args.get('symbol')
        name = lookup(symbol)['name']
        price = request.args.get('price')
        quantity = request.args.get('quantity')
        
        
        
        trade_history = TradeHistory(symbol = symbol, name = name, price = price, action = action, quantity = quantity)
        db.session.add(trade_history)
        current_user.trade_history.append(trade_history)

        # update portfolio
        portfolio = Portfolio.query.with_parent(current_user).all()
        if portfolio:
            # check if the stock already existed
            for company in portfolio:
            # if exists update the averge pruchase price and quantity
                if symbol == company.symbol:
                    # get purchase price and symbol
                    id = company.id
                    stock = Portfolio.query.get_or_404(id)
                    purchase_price = float(stock.purchase_price)
                    own_quantity = float(stock.quantity)

                    # caculate new purchase price and quantity
                    if action =="Buy":
                        new_purchase_price = (purchase_price * own_quantity + float(quantity) * float(price))/(own_quantity + float(quantity))
                        new_own_quantity = own_quantity + float(quantity)
                    else:
                        new_own_quantity = own_quantity - float(quantity)
                        if new_own_quantity == 0:
                            db.session.delete(stock)
                            db.session.commit()
                            return redirect(url_for('home.index'))
        
                        new_purchase_price = (purchase_price*own_quantity - float(quantity) * float(price))/(own_quantity-float(quantity))
                        

                    stock.purchase_price = new_purchase_price
                    stock.quantity =new_own_quantity
                    db.session.commit()
                    return redirect(url_for("home.index"))
            # if not exist in portfolio, create it    
            new_portfolio = Portfolio(symbol = symbol, name = name, purchase_price = price, quantity = quantity)
            current_user.portfolio.append(new_portfolio)
        else:
            new_portfolio = Portfolio(symbol = symbol, name = name, purchase_price = price, quantity = quantity)
            current_user.portfolio.append(new_portfolio)

    db.session.commit()
    return redirect(url_for("home.index"))

@admin_bp.route("/trade_history", methods=['GET', 'POST'])
@login_required
def trade_history():
    # get data from database
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = TradeHistory.query.with_parent(current_user).order_by(TradeHistory.timestamp.desc()).paginate(page, per_page)
    trade_history = pagination.items
    return render_template("admin/trade_history.html", trade_history = trade_history, pagination = pagination)





@admin_bp.route('/watchlist')
@login_required
def show_watchlist():
    form = QuoteForm()
    page = request.args.get('page',1, type= int)
    per_page = 10
    pagination = Watchlist.query.with_parent(current_user).order_by(Watchlist.symbol.asc()).paginate(page, per_page)
    watchlist = pagination.items

    symbols=[] 
    prices =[]         
    changes =[]
    changePercents =[]
    openprices =[]
    highs =[]
    lows =[]
    volumes =[]
    week52Highs =[]
    week52Lows  =[]

    if watchlist:
        for stock in watchlist:
            quote = lookup(stock.symbol)
            
            price= quote["price"]
            symbol= quote["symbol"]
            change= quote["change"]
            changePercent= quote["changePercent"]
            volume= quote["volume"]
            week52High= quote["week52High"]
            week52Low= quote["week52Low"]
            openprice =quote["open"]
            high =quote['high']
            low = quote["low"]

            symbols.append(symbol)
            prices.append(price)         
            changes.append(change)
            changePercents.append(changePercent)
            openprices.append(openprice)
            highs.append(high)
            lows.append(low)
            volumes.append(volume)
            week52Highs.append(week52High)
            week52Lows.append(week52Low)
    return render_template('admin/watchlist.html', watchlist = watchlist, pagination = pagination, form = form,
                            prices = prices, changes = changes, changePercents = changePercents, openprices = openprices,
                            highs = highs, lows = lows, week52Highs = week52Highs, week52Lows = week52Lows, symbols = symbols,
                            volumes = volumes)




@admin_bp.route("/watchlist/new", methods=['GET', 'POST'])
@login_required
def add_to_watchlist():
    
    symbol = request.args.get("symbol")
    symbol_in_watchlist = Watchlist.query.filter_by(symbol = symbol)
    for stock in symbol_in_watchlist:
        if stock.symbol == symbol:
    
            flash("Already existed in your watchlist",'success')
            return redirect(url_for('admin.show_watchlist'))
        
    
    watchlist = Watchlist(symbol = symbol)
    db.session.add(watchlist)
    current_user.watchlist.append(watchlist)
    db.session.commit()
    
    return redirect(url_for('admin.show_watchlist'))

@admin_bp.route("/watchlist/<string:symbol>/delete", methods = ["POST"])
@login_required
def delete_from_watchlist(symbol):
    stocks = Watchlist.query.filter_by(symbol = symbol)
    if stocks:
        id = stocks[0].id
        stock = Watchlist.query.get_or_404(id)
        db.session.delete(stock)
        db.session.commit()
        flash("Delete from your watchlist",'success')
        return redirect_back()
