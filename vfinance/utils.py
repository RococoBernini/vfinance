try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, current_app, url_for, flash
from functools import wraps



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(str(symbol))}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        flash("Please set API_KEY", 'danger')
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"],
            "change": quote["change"],
            "changePercent": quote["changePercent"],
            "volume": quote["volume"],
            "week52High": quote["week52High"],
            "week52Low": quote["week52Low"],
            "open" :quote["open"],
            "high" :quote['high'],
            "low" : quote["low"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def redirect_back(default='home.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
    