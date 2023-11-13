import hashlib
import base64
import pathlib
import os
import uuid
import flask
import requests
import bill_buddies

OPENEI_API_KEY = '7ed6qXM9jqmFRuhtZzMVl5evclf4fCWVS1rwCt7Q'
UTILITY_RATES_ENDPOINT = 'https://api.openei.org/utility_rates?version=latest&api_key={}&format=json&lat={}&lon={}'

# Helper for routing images
@bill_buddies.app.route('/uploads/<path:filename>')
def static_file(filename):
    """Resolve image path."""
    path_app_var = bill_buddies.app.config['UPLOADS_FOLDER']
    if 'logname' not in flask.session:
        flask.abort(403)
    if filename not in os.listdir(path_app_var):
        flask.abort(404)

    return flask.send_from_directory(path_app_var, filename)


# Helper function for hashing password
def hash_password(salt, password):
    """Hash password."""
    hash_obj = hashlib.new('sha512')
    salted = salt + password
    hash_obj.update(salted.encode('utf-8'))
    hashed = hash_obj.hexdigest()
    password_string = "$".join(['sha512', salt, hashed])
    return password_string


def get_lat_lon_from_zipcode(zipcode):
    base_url = "https://geocode.maps.co/search"
    params = {
        "q": zipcode
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            latitude = data[0]['lat']
            longitude = data[0]['lon']
            return latitude, longitude
        else:
            return None, None
    else:
        return None, None


@bill_buddies.app.route('/sorted-utility-rates/<zipcode>')
def get_sorted_utility_rates(zipcode):
    # Convert ZIP code to latitude and longitude
    lat, lon = get_lat_lon_from_zipcode(zipcode)
    if lat is None or lon is None:
        return flask.jsonify({'error': 'Invalid ZIP code or geocoding failed'}), 400
    print(lat, lon)
    # Construct the API request URL using latitude and longitude
    url = UTILITY_RATES_ENDPOINT.format(OPENEI_API_KEY, lat, lon)
    
    # Make the request to OpenEI API
    response = requests.get(url)
    if response.status_code == 200:
        rates = response.json()
        
        # Process and sort rates as needed
        # ...
        
        return flask.jsonify(rates)
    else:
        return flask.jsonify({'error': 'Failed to fetch data'}), response.status_code


# Routing function for /
@bill_buddies.app.route('/')
def show_index():
    """Display / route."""
    # not logged in

    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    # logged in
    # set logname to logname in cookies (flask.session)
    # hard coded logname
    logname = flask.session['logname']
    
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
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_signup'))
    return flask.render_template("aboutus.html")


@bill_buddies.app.route('/explore/')
def show_explore():
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_signup'))
    # connection = bill_buddies.model.get_db()
    context = {
        #"zipcode": zipcode
    }
    return flask.render_template("explore.html", **context)


@bill_buddies.app.route('/login/')
def show_login():
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("login.html")


@bill_buddies.app.route('/signup/')
def show_signup():
    if 'logname' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("signup.html")


@bill_buddies.app.route('/mypage/')
def show_mypage():
    """Display mypage route."""
    # logged in
    # set logname to logname in cookies (flask.session)
    connection = bill_buddies.model.get_db()

    # Hard Coded logname
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['logname']

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


@bill_buddies.app.route('/', methods=['POST'])
def post_zip_index():
    """Login user, helper for post account."""
    target_url = flask.request.args.get('target')
    zipcode = flask.request.form.get('zipcode')
    if not target_url:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target_url)


@bill_buddies.app.route('/explore/', methods=['POST'])
def post_zip_explore():
    """Login user, helper for post account."""
    target_url = flask.request.args.get('target')
    zipcode = flask.request.form.get('zipcode')
    if not target_url:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target_url)


@bill_buddies.app.route('/logout/', methods=['POST'])
def post_logout():
    """Logout users."""
    flask.session.clear()
    return flask.redirect(flask.url_for('show_login'))


@bill_buddies.app.route('/login/', methods=['POST'])
def post_login():
    """Login user, helper for post account."""
    connection = bill_buddies.model.get_db()
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    # fetch users from db
    users = connection.execute(
        "SELECT username, password FROM users"
    )
    users = users.fetchall()

    # username or password is empty
    if not username or not password:
        flask.abort(400)

    # case for username and password authentication fail
    # user does not exist in db
    if username not in [user['username'] for user in users]:
        flask.abort(403)
    # user exists
    else:
        for user in users:
            if user['username'] == username:
                # Hash input with salt obtained from password
                password_hashed = hash_password(
                    user['password'].split('$')[1],
                    password
                    )
                if user['password'] != password_hashed:
                    flask.abort(403)

    # compare hashed password and user input
    # set session
    flask.session['logname'] = username

    target_url = flask.request.args.get('target')

    if not target_url:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target_url)


@bill_buddies.app.route('/signup/', methods=['POST'])
def post_signup():
    """Create user, helper for post account."""
    connection = bill_buddies.model.get_db()
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    fullname = flask.request.form.get("fullname")
    # fetch users from db
    users = connection.execute(
        "SELECT username, password FROM users"
    )
    users = users.fetchall()

    # If any are empty, abort(400)
    if (not username
            or not password):
        flask.abort(400)

    # if user tries to make username that exists in db
    if username in [user['username'] for user in users]:
        flask.abort(409)

    # password hashing
    password_db_string = hash_password(uuid.uuid4().hex, password)

    # insert info into db
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users "
        "(username, password, fullname)"
        "VALUES (?, ?, ?)",
        (username, password_db_string, fullname)
    )

    # log the user in and redirect to target url
    flask.session['logname'] = username

    target_url = flask.request.args.get('target')

    if not target_url:
        return flask.redirect(flask.url_for('show_index'))
    return flask.redirect(target_url)

# @bill_buddies.app.route('/edit/', methods=['POST'])
# def post_account_edit_account(connection, *args):
#     """Edit user account, helper for post account."""
#     (fullname, email, file) = args
#     # fecth users from db
#     users = connection.execute(
#         "SELECT username, password, filename FROM users"
#     )
#     users = users.fetchall()

#     # if user is not logged in abort
#     if 'logname' not in flask.session:
#         flask.abort(403)
#     logname = flask.session['logname']

#     # username or password is empty
#     if not fullname or not email:
#         flask.abort(400)

#     # update user photo into db
#     # compute base name
#     stem = uuid.uuid4().hex
#     suffix = pathlib.Path(file.filename).suffix.lower()
#     uuid_basename = f"{stem}{suffix}"

#     cursor = connection.cursor()
#     # if there is no photo
#     cursor.execute(
#             "UPDATE users SET "
#             "(fullname, email) ="
#             "(?, ?) WHERE username = ?",
#             (fullname, email, logname)
#     )
       
#     target_url = flask.request.args.get('target')

#     if not target_url:
#         return flask.redirect(flask.url_for('show_index'))
#     return flask.redirect(target_url)

