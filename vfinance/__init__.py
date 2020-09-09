import logging
import os

from logging.handlers import SMTPHandler, RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError


from vfinance.blueprints.admin import admin_bp
from vfinance.blueprints.auth import auth_bp
from vfinance.blueprints.home import home_bp
from vfinance.utils import usd, lookup
from vfinance.settings import config
from vfinance.extensions import bootstrap, db, login_manager, toolbar, moment, csrf
from vfinance.models import User, TradeHistory, Watchlist



basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
config_name = os.getenv("FLASK_CONFIG", "develpement")

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

def create_app(config_name = None):
    if config_name == None:
        config_name = os.getenv("FLASK_CONFIG", "development")
    
    app = Flask('vfinance')
    app.config.from_object(config[config_name])
    app.jinja_env.filters["usd"] = usd
    app.jinja_env.globals["lookup"] = lookup
    app.jinja_env.auto_reload = True


    register_blueprints(app)
    register_commands(app)
    register_extensions(app)
    register_template_context(app)
    return app


def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(admin_bp, url_prefix = "/admin")
    app.register_blueprint(auth_bp, url_prefix = "/auth")

def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)

def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        pass

def register_template_context(app):
    @app.context_processor
    def make_template_context():
        user = User.query.first()
        if current_user.is_authenticated:
            watchlist = Watchlist.query.with_parent(current_user).order_by(Watchlist.symbol.asc()).all()
            priceInWatchlist = []
            if watchlist:
                for stock in watchlist:
                    quote = lookup(stock.symbol)
                    price = quote['price']
                    priceInWatchlist.append(price)


        
                return dict(
                    user = user,
                    watchlist = watchlist,
                    priceInWatchlist = priceInWatchlist
                    
                )
            else:
                return dicd(user = user)
        else:
            return dict(user = user,)





def register_commands(app):
    @app.cli.command()
    @click.option('--user', default = 10, help='Quantity of accounts, defalult is 10')
    def forge(user):
        from vfinance.fakes import fake_user

        db.drop_all()
        db.create_all()

        click.echo("Generating the User Account...")
        fake_user()

        click.echo("Done")


    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        if drop:
            click.confirm("This operation will delete the database, do you want to continue?", abort=True)
            db.drop_all()
            click.echo("Drop tables.")
        db.create_all()
        click.echo("Initialized database.")