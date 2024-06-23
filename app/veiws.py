from app import app
from flask import render_template, request, url_for, flash, redirect, session
import mysql.connector
import datetime
from app.input_handler import *
import dotenv
import os


def user_update_query(attribute, attr_name):
    if isinstance(attribute, str):
        query = "UPDATE NormalUser SET {} = '{}' WHERE UserID= {}".format(attr_name, attribute, session['id'])
    else:
        query = "UPDATE NormalUser SET {} = {} WHERE UserID= {}".format(attr_name, attribute, session['id'])
    print('query', query)
    updating = execute_update_query(query)
    if updating == 'Duplicate':
        flash('{} is duplicate.Try agin'.format(attr_name))
        return updating
    elif updating == 'Error':
        flash('Updating was incomplete. Try agin'.format(attr_name))
        return updating
    else:
        return updating


def execute_update_query(query):
    try:
        cursor.execute(query)
        cnx.commit()
        return 'Done'
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        if 'Duplicate' in str(err):
            return 'Duplicate'
        return 'Error'


def execute_insert_query(query, data):
    try:
        cursor.execute(query, data)
        cnx.commit()
        return 'Done', int(cursor.lastrowid)
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        if 'Duplicate entry' in str(err):
            return 'Duplicate', -1


def execute_read_query(query, fetch_all):
    try:
        cursor.execute(query)
        if fetch_all:
            return cursor.fetchall()
        else:
            return cursor.fetchone()

    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


dotenv.load_dotenv(override=True)
cnx = mysql.connector.connect(user='root', password=os.getenv('SQL_PASS'),
                              host='127.0.0.1',
                              database='Divar')
cursor = cnx.cursor(dictionary=True)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/signup/", methods=['GET', 'POST'])
def sign_up():
    cities = execute_read_query("SELECT City FROM Region", True)
    add_user = ("INSERT INTO NormalUser"
                "(IsActive, FirstName, LastName, RegisteredAt, Email, Phone, City, Street, House_num) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

    print(cities)

    if request.method == 'POST':
        in_f_name = handle_null_str(request.form['inFName'])
        in_l_name = handle_null_str(request.form['inLName'])
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])
        in_city = handle_null_str(request.form['uCity'])
        in_street = handle_null_str(request.form['inStreet'])
        in_house_num = handle_null_int(request.form['inHouseNum'])

        data_n_user = (1, in_f_name, in_l_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), in_email,
                       in_phone, in_city, in_street, in_house_num)

        # Check all invalid and incomplete user data
        if not in_email and not in_phone:
            flash('One of Email or Phone is required!')
            return redirect(url_for('sign_up'))
        elif not in_f_name or not in_l_name:
            flash('You should enter yor name completely!')
            return redirect(url_for('sign_up'))
        elif not email_checker(in_email):
            flash("Invalid Email")
            return redirect(url_for('sign_up'))
        elif not phone_checker(in_phone):
            flash("Invalid Phone Number")
            return redirect(url_for('sign_up'))
        elif in_street is None and in_house_num is not None:
            flash('Please enter street name!')
            return redirect(url_for('sign_up'))
        else:
            user_insertion, user_id = execute_insert_query(add_user, data_n_user)
            if user_insertion == 'Done':
                session['logged_in'] = True
                session['id'] = user_id
                print(session['id'])
                return redirect(url_for('home'))
            else:
                flash('email or phone is duplicate.Try another')
                return redirect(url_for('sign_up'))
    else:   # GET
        return render_template("signup.html", cities=cities)


@app.route('/logout')
def logout():
    session.pop('id', None)
    session.pop('logged_in', None)
    # session['logged_in'] = False
    return redirect(url_for('index'))


@app.route("/home/", methods=['GET', 'POST'])
def home():
    # TODO: filter advertises
    if 'logged_in' in session:
        recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID), AdCatID, Title,"
                                        "Price, Descriptions, Subtitle, City, Street, HouseNum, CreatedAt"
                                        " ,Images.ImagePath FROM divar.Advertise JOIN divar.Images "
                                        "ON Advertise.AdID = Images.AdID Order BY CreatedAt DESC", True)

        if request.method == 'POST':
            searched = str(request.form['searchString'])
            print(searched)
            recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID), AdCatID, Title, Price, "
                                            "Descriptions, Subtitle, City, Street, HouseNum, CreatedAt,"
                                            "Images.ImagePath  FROM divar.Advertise JOIN divar.Images "
                                            "ON Advertise.AdID = Images.AdID "
                                            "WHERE Advertise.Title LIKE '%{}%'"
                                            "Order BY CreatedAt DESC".format(searched), True)

        for i in range(len(recent_ads)):
            delta = datetime.datetime.now() - recent_ads[i]['CreatedAt']
            recent_ads[i]['DaysPast'] = delta.days

        page = request.args.get('page', 1, type=int)
        per_page = 12
        start = (page - 1) * per_page
        end = start + per_page
        total_pages = (len(recent_ads) + per_page - 1) // per_page
        items_on_page = recent_ads[start:end]
        print(recent_ads)
        return render_template('home.html', items=items_on_page, total_pages=total_pages, page=page)

    else:
        return redirect(url_for('sign_up'))


@app.route('/item/<int:adv_id>')
def advertise_detail(adv_id):
    # check if this is here
    if 'logged_in' in session:
        execute_insert_query("INSERT INTO Visit (AdID, UserID) VALUES (%s, %s)", (adv_id, session['id']))
        advertise = execute_read_query("SELECT * FROM Advertise WHERE AdID={}".format(adv_id), False)
        advertise_images = execute_read_query("SELECT * FROM Images WHERE AdID={}".format(adv_id), True)
        advertise_images = images_path_handler(advertise_images)
        if advertise is None:
            return "Item not found", 404
        return render_template('ads_detail.html', item=advertise, ad_images=advertise_images)
    else:
        return redirect(url_for('sign_up'))


@app.route("/registerAd/", methods=['GET', 'POST'])
def register_ad():
    if 'logged_in' in session:
        categories = execute_read_query("SELECT * FROM AdCat", True)
        cities = execute_read_query("SELECT City FROM Region", True)
        add_advertise = ("INSERT INTO Advertise (CreatorID, UserMade, AdCatID, Title, Price, Descriptions,"
                         " Subtitle, City, Street, HouseNum, CreatedAt, UpdatedAt) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        print(categories)
        if request.method == 'POST':
            ad_title = handle_null_str(request.form['adTitle'])
            ad_subtitle = handle_null_str(request.form['adSubTitle'])
            ad_description = handle_null_str(request.form['adDesc'])
            ad_price = handle_null_float(request.form['adPrice'])
            # ad_image = handle_null_str(request.form['adImage'])
            ad_cat = handle_null_str(request.form['adCat'])
            ad_city = handle_null_str(request.form['adCity'])
            ad_street = handle_null_str(request.form['adStreet'])
            ad_house_num = handle_null_str(request.form['adHouseNum'])
            print(session['id'])
            data_n_ad = (session['id'], True, ad_cat, ad_title, ad_price, ad_description, ad_subtitle, ad_city,
                         ad_street, ad_house_num, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Check all invalid and incomplete user data
            if not ad_title:
                flash("Please enter Title")
                return redirect(url_for('register_ad'))
            elif not ad_price:
                flash('Please enter the Price')
                return redirect(url_for('register_ad'))
            elif ad_street is None and ad_house_num is not None:
                flash('Please enter street name!')
                return redirect(url_for('register_ad'))
            else:
                ad_insertion, ad_id = execute_insert_query(add_advertise, data_n_ad)
                if ad_insertion == 'Done':
                    return redirect(url_for('home'))
                else:
                    # not sure
                    flash('email or phone is duplicate.Try another')
                    return redirect(url_for('sign_up'))
        else:  # GET
            return render_template("registerAd.html", cities=cities, categories=categories)
    else:
        return redirect(url_for('sign_up'))


@app.route("/registerBusiness/", methods=['GET', 'POST'])
def register_bus():
    if 'logged_in' in session:
        categories = execute_read_query("SELECT * FROM BusCat", True)
        cities = execute_read_query("SELECT City FROM Region", True)
        add_business = ("INSERT INTO Business (UserID, IsActive, BusName,"
                        " BusCatID, City, Street, HouseNum) VALUES (%s, %s, %s, %s, %s, %s, %s)")

        if request.method == 'POST':
            bus_name = handle_null_str(request.form['busName'])
            bus_cat = handle_null_int(request.form['busCat'])
            bus_city = handle_null_str(request.form['busCity'])
            bus_street = handle_null_str(request.form['busStreet'])
            bus_house_num = handle_null_int(request.form['busHouseNum'])
            data_n_business = (session['id'], True, bus_name, bus_cat, bus_city, bus_street, bus_house_num)

            # Check all invalid and incomplete user data
            if not bus_name:
                flash('Please Enter your Business Name')
                return redirect(url_for('register_bus'))
            elif bus_street is None and bus_house_num is not None:
                flash('Please enter street name!')
                return redirect(url_for('register_bus'))
            else:
                bus_insertion, bus_id = execute_insert_query(add_business, data_n_business)
                if bus_insertion == 'Done':
                    return redirect(url_for('home'))
                else:
                    flash('Business Name is duplicate.Try another')
                    return redirect(url_for('register_bus'))
        else:  # GET
            return render_template("registerBus.html", cities=cities, categories=categories)
    else:
        return redirect(url_for('sign_up'))


@app.route("/reportAd/<int:ad_id>", methods=['GET', 'POST'])
def report_ad(ad_id):
    if 'logged_in' in session:
        categories = execute_read_query("SELECT * FROM RepCat", True)
        add_report = ("INSERT INTO AdReport (AdID, UserID, RepCatID, Content) "
                      "VALUES (%s, %s, %s, %s)")
        print(categories)
        if request.method == 'POST':
            rep_cat = handle_null_int(request.form['repCat'])
            rep_content = handle_null_str(request.form['repContent'])

            data_n_report = (ad_id, session['id'], rep_cat, rep_content)
            execute_insert_query(add_report, data_n_report)
            return redirect(url_for('home'))

        else:  # GET
            return render_template("reportAd.html", categories=categories, AdID=ad_id)
    else:
        return redirect(url_for('sign_up'))


@app.route("/updateProfile/", methods=['GET', 'POST'])
def update_profile():
    if 'logged_in' in session:
        cities = execute_read_query("SELECT City FROM Region", True)
        current_user = execute_read_query("SELECT FirstName, LastName, Email, Phone, City, Street,"
                                          " House_num FROM NormalUser WHERE UserID = {}"
                                          .format(session['id']), False)

        print(current_user)
        if request.method == 'POST':
            prof_f_name = handle_null_str(request.form['inFName'])
            prof_l_name = handle_null_str(request.form['inLName'])
            prof_phone = handle_null_str(request.form['inPhone'])
            prof_email = handle_null_str(request.form['inEmail'])
            prof_city = handle_null_str(request.form['uCity'])
            prof_street = handle_null_str(request.form['inStreet'])
            prof_house_num = handle_null_int(request.form['inHouseNum'])

            # Check email first
            if prof_email:
                if not email_checker(prof_email):
                    flash("Invalid Email")
                    return redirect(url_for('update_profile'))
                else:
                    if user_update_query(prof_email, 'Email') != 'Done':
                        return redirect(url_for('update_profile'))
            # Check phone first
            if prof_phone:
                if not phone_checker(prof_phone):
                    flash("Invalid Phone Number")
                    return redirect(url_for('update_profile'))
                else:
                    if user_update_query(prof_phone, 'Phone') != 'Done':
                        return redirect(url_for('update_profile'))

            profile = (prof_f_name, prof_l_name, prof_city, prof_street, prof_house_num)
            print('profile', profile)
            names = ('FirstName', 'LastName', 'City', 'Street', 'House_num')
            for i in range(len(profile)):
                if profile[i] is not None and current_user[names[i]] != profile[i]:
                    print(profile[i])
                    if user_update_query(profile[i], names[i]) != 'Done':
                        return redirect(url_for('update_profile'))

            return redirect(url_for('home'))

        else:  # GET
            return render_template("updateProfile.html", cities=cities, curr=current_user)
    else:
        return redirect(url_for('sign_up'))


# incomplete
@app.route("/advertiseStatus/")
def advertise_status():
    if 'logged_in' in session:
        # TODO : Complete the query to have status or handle in back or front to have type of status
        ads = execute_read_query("SELECT AdID, Title, Price, Descriptions, Subtitle, City, Street, HouseNum,"
                                 "CreatedAt, StatusComment, statID FROM divar.AdStatus JOIN divar.Advertise on "
                                 "AdStatus.AdID = Advertise.AdID WHERE UserID = {}"
                                 .format(session['id']), False)

        print(ads)
        if ads is None:
            flash("You don't have any advertise")
            return redirect(url_for('home'))

        dict_ads = []
        for i in range(len(ads)):
            advertise = ads[i]
            visit_number = execute_read_query("SELECT COUNT(UserID) FROM divar.Visit WHERE AdID = {}"
                                              .format(advertise[0]), False)

            print(visit_number)
            advertise.append(visit_number)
            # method convert a list to a dictionary to better handle in html (you can see usage in user update route)
            advertise = convert_to_dict(advertise, ('AdID', 'Title', 'Price', 'Descriptions', 'Subtitle',
                                                    'City', 'Street', 'HouseNum', 'CreatedAt', 'StatusComment',
                                                    'statID'), [])
            dict_ads.append(advertise)

        # TODO: pass dict_ads to front to have complete data and also
        # TODO: (front) complete page so that each advertise be more specific and big
        return render_template('status.html', items=ads)
    else:
        return redirect(url_for('sign_up'))
