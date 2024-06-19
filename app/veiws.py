from app import app
from flask import render_template, request, url_for, flash, redirect, session
import mysql.connector
from datetime import datetime
from app.input_handler import *
import dotenv
import os


def execute_insert_query(query, data):
    try:
        cursor.execute(query, data)
        cnx.commit()
        return 'Done', int(cursor.lastrowid)
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        if 'Duplicate entry' in str(err):
            return 'Duplicate', -1


def execute_read_query(query):
    try:
        cursor.execute(query)
        out = cursor.fetchall()
        return out
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


dotenv.load_dotenv(override=True)
cnx = mysql.connector.connect(user='root', password=os.getenv('SQL_PASS'),
                              host='127.0.0.1',
                              database='Divar')
cursor = cnx.cursor()


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/home/")
def home():
    # TODO: complete navbar for home page and filter advertises
    if 'logged_in' in session:
        recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID), CreatorID, UserMade, AdCatID, Title,"
                                        " Price, Descriptions, Subtitle, City, Street, HouseNum, CreatedAt, UpdatedAt,"
                                        " Images.ImagePath FROM divar.Advertise JOIN divar.Images "
                                        "ON Advertise.AdID = Images.AdID Order BY CreatedAt")

        return render_template('home.html', items=recent_ads[0:10])
    else:
        return redirect(url_for('sign_up'))


@app.route("/signup/", methods=['GET', 'POST'])
def sign_up():
    cities = execute_read_query("SELECT City FROM Region")
    add_user = ("INSERT INTO NormalUser"
                "(IsActive, FirstName, LastName, RegisteredAt, Email, Phone, City, Street, House_num) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

    if request.method == 'POST':
        in_f_name = handle_null_str(request.form['inFName'])
        in_l_name = handle_null_str(request.form['inLName'])
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])
        in_city = handle_null_str(request.form['uCity'])
        in_street = handle_null_str(request.form['inStreet'])
        in_house_num = handle_null_int(request.form['inHouseNum'])

        data_n_user = (1, in_f_name, in_l_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), in_email,
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

                return redirect(url_for('home'))
            else:
                flash('email or phone is duplicate.Try another')
                return redirect(url_for('sign_up'))
    else:   # GET
        return render_template("signup.html", cities=cities)


@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))


@app.route('/item/<int:adv_id>')
def advertise_detail(adv_id):
    # check if this is here
    if 'logged_in' in session:
        execute_insert_query("INSERT INTO Visit (AdID, UserID) VALUES (%s, %s)", (adv_id, session['id']))
        advertise = execute_read_query("SELECT * FROM Advertise WHERE AdID={}".format(adv_id))
        advertise_images = execute_read_query("SELECT * FROM Images WHERE AdID={}".format(adv_id))
        advertise_images = images_path_handler(advertise_images)
        if advertise is None:
            return "Item not found", 404
        return render_template('ads_detail.html', item=advertise[0], ad_images=advertise_images)
    else:
        return redirect(url_for('sign_up'))


@app.route("/registerAd/", methods=['GET', 'POST'])
def register_ad():
    if 'logged_in' in session:
        categories = execute_read_query("SELECT * FROM AdCat")
        cities = execute_read_query("SELECT City FROM Region")
        add_advertise = ("INSERT INTO Advertise (CreatorID, UserMade, AdCatID, Title, Price, Descriptions,"
                         " Subtitle, City, Street, HouseNum, CreatedAt, UpdatedAt) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

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

            data_n_ad = (session['id'], True, ad_cat, ad_title, ad_price, ad_description, ad_subtitle, ad_city,
                         ad_street, ad_house_num, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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

# TODO : DEBUG THIS BLOODY ERROR
#incomplete
# error in executing insert query line 203
@app.route("/registerBusiness/", methods=['GET', 'POST'])
def register_bus():
    if 'logged_in' in session:
        categories = execute_read_query("SELECT * FROM BusCat")
        cities = execute_read_query("SELECT City FROM Region")
        add_business = ("INSERT INTO Business"
                    "(UserID, IsActive, BusName, BusCatID, City, Street, HouseNum) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)")

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

#TODO : I WAS TIRED TO CHECK HOW TO PASS DATA TO NEW PAGE SOMBODEY PLEASSE CHECK THIS
#incomplete
# it doesn't have the ad id
@app.route("/reportAd/<int:ad_id>", methods=['GET', 'POST'])
def report_ad(ad_id):
    if 'logged_in' in session:
        categories = execute_read_query("SELECT * FROM RepCat")
        add_report = ("INSERT INTO AdReport"
                    "(AdID, UserID, RepCatID, Content) "
                    "VALUES (%s, %s, %s, %s)")

        if request.method == 'POST':
            rep_cat = handle_null_int(request.form['repCat'])
            rep_content = handle_null_str(request.form['repContent'])

            data_n_report = (ad_id, session['id'], rep_cat, rep_content)
            rep_insertion, rep_id = execute_insert_query(add_report, data_n_report)
            return redirect(url_for('home'))

        else:  # GET
            return render_template("reportAd.html", categories=categories, AdID=ad_id)
    else:
        return redirect(url_for('sign_up'))

# TODO: FIX THIS FUCKING API AND DEBUG ERRORS. QUERIES ARE WRONG FORMAT
# incomplete
# a lot of things to fix
@app.route("/updateProfile/", methods=['GET', 'POST'])
def update_profile():
    if 'logged_in' in session:
        cities = execute_read_query("SELECT City FROM Region")

        if request.method == 'POST':
            prof_f_name = handle_null_str(request.form['inFName'])
            prof_l_name = handle_null_str(request.form['inLName'])
            prof_phone = handle_null_str(request.form['inPhone'])
            prof_email = handle_null_str(request.form['inEmail'])
            prof_city = handle_null_str(request.form['uCity'])
            prof_street = handle_null_str(request.form['inStreet'])
            prof_house_num = handle_null_int(request.form['inHouseNum'])

            # Check all invalid and incomplete user data
            if prof_f_name:
                query = ("UPDATE NormalUser"
                         "SET FirstName = (%s)"
                         "WHERE UserID= (%s)")
                data=(prof_f_name, session['id'])
                updating, user_id = execute_insert_query(query, data)
            if prof_l_name:
                query = ("UPDATE NormalUser"
                         "SET  LastName= %s"
                         "WHERE UserID= %s")
                data=(prof_l_name, session['id'])
                updating, user_id = execute_insert_query(query, data)
            if prof_email:
                if not email_checker(prof_email):
                    flash("Invalid Email")
                    return redirect(url_for('update_profile'))
                else:
                    query = ("UPDATE NormalUser"
                             "SET Email = %s"
                             "WHERE UserID= %s")
                    data=(prof_email, session['id'])
                    updating, user_id = execute_insert_query(query, data)
                if updating == 'Done':
                    return redirect(url_for('home'))
                else:
                    flash('Email is Duplicate.Try another')
                    return redirect(url_for('update_profile'))
            if prof_phone:
                if not phone_checker(prof_phone):
                    flash("Invalid Phone Number")
                    return redirect(url_for('update_profile'))
                else:
                    query = ("UPDATE NormalUser"
                             "SET Phone = %s"
                             "WHERE UserID= %s")
                    data = (prof_email, session['id'])
                    updating, user_id = execute_insert_query(query, data)
                    if updating == 'Done':
                        return redirect(url_for('home'))
                    else:
                        flash('Phone Number is duplicate.Try another')
                        return redirect(url_for('update_profile'))
            if prof_city:
                query = ("UPDATE NormalUser"
                         "SET City = %s"
                         "WHERE UserID= %s")
                data = (prof_city, session['id'])
                updating, user_id = execute_insert_query(query, data)
            if prof_street:
                query = ("UPDATE NormalUser"
                         "SET Street = %s"
                         "WHERE UserID= %s")
                data = (prof_street, session['id'])
                updating, user_id = execute_insert_query(query, data)
            if prof_house_num:
                query = ("UPDATE NormalUser"
                         "SET House_num = %s"
                         "WHERE UserID= %s")
                data = (prof_house_num, session['id'])
                updating, user_id = execute_insert_query(query, data)
        else:  # GET
            return render_template("updateProfile.html", cities=cities)
    else:
        return redirect(url_for('sign_up'))