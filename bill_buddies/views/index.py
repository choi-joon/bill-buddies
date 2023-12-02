import hashlib
import base64
import pathlib
import os
import uuid
import flask
import requests
import datetime
import bill_buddies
import random

NREL_API_KEY = 'ChvLonWumEHOLKF7Q5gCwyoVq6giJ20ipk3RdeZm'
UTILITY_RATES_ENDPOINT = 'https://developer.nrel.gov/api/utility_rates/v3.json'
RADIUS = 50

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

@bill_buddies.app.route('/explore/', methods=['POST'])
def process_zipcode():
    zipcode = flask.request.form['zipcode']
    # Call the function to process the ZIP code and get data
    sorted_utility_rates = get_sorted_utility_rates(zipcode)
    sorted_utility_rates = {frozenset(item.items()) : 
            item for item in sorted_utility_rates}.values()
    context = {
        "zipcode": zipcode,
        "util_list": sorted_utility_rates
    }
    print(sorted_utility_rates)
    # Render the explore.html with the sorted utility rates
    return flask.render_template('explore.html', **context)

def get_sorted_utility_rates(zipcode):
    lat, lon = get_lat_lon_from_zipcode(zipcode)
    if lat is None or lon is None:
        return flask.jsonify({'error': 'Invalid ZIP code'}), 400
    params = {
        'api_key' : NREL_API_KEY,
        'lat': lat,
        'lon': lon,
        'radius': RADIUS,
    }
    response = requests.get(UTILITY_RATES_ENDPOINT, params=params)
    if response.status_code == 200:
        data = response.json()
        outputs = data['outputs']
        utility_info_list = [
            {
                'utility_name': name,
                'rate': round(max(outputs.get(rate_type, 0) * random.uniform(1,2) for rate_type in ['commercial', 'industrial', 'residential']), 3)
            }
            for name in outputs['utility_name'].split('|')
        ]
        sorted_utility_rates = sorted(utility_info_list, key=lambda x: x['rate'])
        return sorted_utility_rates
        return flask.jsonify({'sorted_utility_rates': sorted_utility_rates})
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

    # Add database info to context
    context = {
        "logname": logname,
    }
    return flask.render_template("index.html", **context)


@bill_buddies.app.route('/aboutus/')
def show_aboutus():
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_signup'))
    return flask.render_template("aboutus.html")


@bill_buddies.app.route('/explore/', methods=['GET', 'POST'])
@bill_buddies.app.route('/', methods=['GET', 'POST'])
def show_explore():
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_signup'))
    # connection = bill_buddies.model.get_db()
    if flask.request.method == 'POST':
        # Capture the zipcode from the form
        zipcode = str(flask.request.form['zipcode'])
        if zipcode == "48104":
            comp1 = {
                "company": "DTE",
                "price": "$80",
                "description": "Monthly gas/electric price"
            }
            comp2 = {
                "company": "Michigan Water",
                "price": "$33.50",
                "description": "Monthly water price"
            }
            comp3 = {
                "company": "Xfinity",
                "price": "$45",
                "description": "Monthly wifi/connection price"
            }
            comp4 = {
                "company": "Consumers Energy",
                "price": "$185",
                "description": "Monthly gas/electric price"
            }
            comp5 = {
                "company": "Upper Michigan Water Company",
                "price": "$60",
                "description": "Monthly water price"
            }
            context = {
                "zipcode": zipcode,
                "util_list": [comp1, comp4, comp2, comp5, comp3]
            }
            return flask.render_template("explore.html", **context)
        else:
            # 1210 South Indiana Avenue, Chicago, IL 60605
            comp1 = {
                "company": "ComEd",
                "price": "$158",
                "description": "Monthly gas/electric price"
            }
            comp2 = {
                "company": "Department of Water Management",
                "price": "$25",
                "description": "Monthly water price"
            }
            comp3 = {
                "company": "AT&T",
                "price": "$35",
                "description": "Monthly Wifi/Connection price"
            }
            context = {
                "zipcode": zipcode,
                "util_list": [comp1, comp2, comp3]
            }
            return flask.render_template("explore.html", **context)
    context = {}
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


@bill_buddies.app.route('/mypage/', methods=['GET', 'POST'])
def show_mypage():
    """Display mypage route."""
    # logged in
    # set logname to logname in cookies (flask.session)
    connection = bill_buddies.model.get_db()

    # Hard Coded logname
    if 'logname' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    logname = flask.session['logname']

    current_month = datetime.datetime.now().strftime('%Y-%m')
    monthly_bill = connection.execute(
        "SELECT SUM(electricity_bill + water_bill + gas_bill + garbage_bill) \
        FROM usage WHERE strftime('%Y-%m', month) = ?  AND username = ?",
        (current_month, logname)
    )
    monthly_bill = monthly_bill.fetchall()

    average_utility_bill = connection.execute(
        """
        SELECT AVG(total)
        FROM (
            SELECT strftime('%Y-%m', month) AS year_month, SUM(electricity_bill + water_bill + gas_bill + garbage_bill) AS total
            FROM usage
            WHERE username = ?
            GROUP BY year_month
        ) AS monthly_totals      
        """, (logname,)
    )

    average_utility_bill = average_utility_bill.fetchall()

    # Add database info to context
    # context = {
    #     "logname": logname,
    #     "monthly_bill": monthly_bill,
    #     "average_utility_bill": average_utility_bill,
    # }
    
    tips_water = [
        "Fix Leaks Promptly: A dripping faucet or leaking toilet can waste a significant amount of water over time.",
        "Install Water-Efficient Fixtures: Low-flow showerheads, faucets, and dual-flush toilets can reduce water consumption significantly.",
        "Shorten Showers: Taking shorter showers can save a substantial amount of water. Even reducing your shower time by a minute or two can make a difference.",
        "Turn Off the Tap: Don’t leave the water running while brushing your teeth or shaving.",
        "Use Dishwashers and Washing Machines Wisely: Only run them when they are full. Choose the eco-setting if available.",
        "Water Plants Wisely: Water your garden during the cooler parts of the day to reduce evaporation. Use drought-resistant plants.",
        "Reuse Greywater: Consider systems that allow you to reuse water from sinks and showers for toilets or gardening.",
    ]
    tips_electricity =[
        "Switch to LED Bulbs: LED light bulbs use up to 75% less energy than traditional incandescent bulbs and last much longer.",
        "Unplug Electronics: Devices still consume power when they're off but plugged in. Unplug them or use a power strip to turn off multiple devices at once.",
        "Use Smart Thermostats: These can optimize heating and cooling, reducing energy use.",
        "Air Dry Clothes and Dishes: Avoid using the dryer for clothes and the heat-dry setting on your dishwasher.",
        "Maintain Appliances: Regular maintenance ensures that appliances like refrigerators and air conditioners run efficiently.",
        "Seal Windows and Doors: Prevent air leaks by sealing drafts, which can reduce heating and cooling costs.",
        "Use Energy-Efficient Appliances: When replacing appliances, look for those with a high energy-efficiency rating.",
        "Practice Efficient Cooking: Use lids on pots to cook food faster and consider using a microwave or toaster oven for smaller meals."
    ]
    tips_trash = [
        "Reduce, Reuse, Recycle: This is the golden rule. Always think about whether you can reduce your use of an item, reuse something instead of throwing it away, or recycle it.",
        "Composting: Start composting organic waste like food scraps and yard waste. This can significantly reduce the amount of garbage you produce and provide you with excellent soil for gardening.",
        "Buy in Bulk: Purchasing items in bulk can reduce packaging waste. Be sure to bring your own reusable containers or bags.",
        "Avoid Single-Use Items: Opt for reusable items instead of disposable ones. For example, use cloth napkins, rechargeable batteries, and refillable water bottles.",
        "Recycle Properly: Make sure you are aware of your local recycling rules and recycle as much as possible. This includes paper, cardboard, plastic, glass, and metal.",
        "Donate or Sell Unused Items: Instead of throwing away items you no longer need, consider donating them to charity or selling them. This can include clothes, furniture, electronics, and more.",
    ]
    if flask.request.method == 'POST':
        water = int(flask.request.form.get('water'))
        elec = int(flask.request.form.get('electricity'))
        hc = int(flask.request.form.get('heatcooling'))
        trash = int(flask.request.form.get('trash'))
        internet = int(flask.request.form.get('internet'))
        phone = int(flask.request.form.get('phone'))
        sum = water + elec + hc + trash + internet + phone
        context = {
            "price": sum,
            "water": water,
            "electricity": elec,
            "hc": hc,
            "trash": trash,
            "internet": internet,
            "phone": phone,
            "tips": [tips_water[random.randint(0,6)], tips_electricity[random.randint(0,7)], tips_trash[random.randint(0,5)]]
        }
    else:
        context = {
            "price": 185,
            "water": 30,
            "electricity": 45,
            "hc": 25,
            "trash": 10,
            "internet": 30,
            "phone": 30,
            "tips": [tips_water[random.randint(0,6)], tips_electricity[random.randint(0,7)], tips_trash[random.randint(0,5)]]
        }
    return flask.render_template("mypage.html", **context)


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


@bill_buddies.app.route('/logout/')
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

@bill_buddies.app.route('/add-usage/', methods=['POST'])
def add_monthly_usage():
    try:
        connection = bill_buddies.model.get_db()
        if 'logname' not in flask.session:
            return flask.redirect(flask.url_for('show_login'))
        logname = flask.session['logname']

        month = flask.request.form.get('month')
        electricity_usage = flask.request.form.get('electricity_bill')
        water_usage = flask.request.form.get('water_bill')
        gas_usage = flask.request.form.get('gas_bill')
        garbage_usage = flask.request.form.get('garbage_bill')

        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO usage (username, month, electricity_bill, water_bill, gas_bill, garbage_bill)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (logname, month, electricity_usage, water_usage, gas_usage, garbage_usage)
        )
        connection.commit()
        cursor.close()
        return flask.jsonify({'msg': 'success'})
    except Exception as e:
        return flask.jsonify({'error': str(e)}), 400
