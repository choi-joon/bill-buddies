import hashlib
import base64
import pathlib
import os
import uuid
import flask
import requests
import bill_buddies

OPENEI_API_KEY = '7ed6qXM9jqmFRuhtZzMVl5evclf4fCWVS1rwCt7Q'
UTILITY_RATES_ENDPOINT = 'https://api.openei.org/utility_rates?version=latest&api_key={}&format=json&zipcode={}'

# Helper function for hashing password
def hash_password(salt, password):
    """Hash password."""
    hash_obj = hashlib.new('sha512')
    salted = salt + password
    hash_obj.update(salted.encode('utf-8'))
    hashed = hash_obj.hexdigest()
    password_string = "$".join(['sha512', salt, hashed])
    return password_string


def authenticate():
    """Authenticate logname."""
    if 'Authorization' in flask.request.headers:
        auth = flask.request.headers.get('Authorization').split(" ")[1]
        decoded = base64.b64decode(auth, altchars=None, validate=False)
        username = decoded.decode().split(':')[0]
        password = decoded.decode().split(':')[1]
        connection = bill_buddies.model.get_db()
        users = connection.execute(
            "SELECT username, password FROM users"
        )
        users = users.fetchall()
        # username or password is empty
        if not username or not password:
            return None
        # user exists
        for user in users:
            if user['username'] == username:
                # Hash input with salt obtained from password
                password_hashed = hash_password(
                    user['password'].split('$')[1],
                    password
                )
                if user['password'] == password_hashed:
                    return username
        return None
    if 'logname' in flask.session:
        return flask.session['logname']
    return None


@bill_buddies.app.route('/sorted-utility-rates/<zipcode>')
def get_sorted_utility_rates(zipcode):
    # Construct the API request URL
    url = UTILITY_RATES_ENDPOINT.format(OPENEI_API_KEY, zipcode)
    
    # Make the request to OpenEI API
    response = requests.get(url)
    if response.status_code == 200:
        rates = response.json()
        
        # Assuming 'rates' is a list of dictionaries that contain a 'rate' key
        # Sort the rates by the 'rate' key
        sorted_rates = sorted(rates, key=lambda x: x['rate'])
        
        return flask.jsonify(sorted_rates)
    else:
        return flask.jsonify({'error': 'Failed to fetch data'}), response.status_code

# Routing function for /
@bill_buddies.app.route('/')
def show_index():
    """Display / route."""
    # not logged in

    # logged in
    # set logname to logname in cookies (flask.session)
    logname = authenticate()
    
    if not logname:
        return flask.redirect(flask.url_for('show_login'))

    # Connect to database
    connection = bill_buddies.model.get_db()

    # Query users
    users = connection.execute(
        "SELECT username FROM users"
    )
    users = users.fetchall()

    # Query utility rates
    rates = connection.execute(
        "SELECT * FROM utility_rates"
    )
    rates = rates.fetchall()

    # Add database info to context
    context = {
        "logname": logname,
        "rates": rates,
    }
    return flask.render_template("index.html", **context)


@bill_buddies.app.route('/aboutus/')
def show_aboutus():
    return flask.render_template("aboutus.html")


@bill_buddies.app.route('/explore/')
def show_explore():
    return flask.render_template("explore.html")


@bill_buddies.app.route('/accounts/login/')
def show_login():
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@bill_buddies.app.route('/accounts/signup/')
def show_signup():
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("signup.html")


@bill_buddies.app.route('/mypage/')
def show_mypage():
    """Display mypage route."""
    # logged in
    # set logname to logname in cookies (flask.session)
    logname = authenticate()
    if not logname:
        return flask.redirect(flask.url_for('show_login'))
    # Connect to database
    connection = bill_buddies.model.get_db()

    # Query utility rates
    rate = connection.execute(
        "SELECT * FROM utility_rates WHERE username = ?", (logname,)
    )
    rate = rate.fetchall()

    # Add database info to context
    context = {
        "logname": logname,
        "rates": rate,
    }
    return flask.render_template("mypage.html")