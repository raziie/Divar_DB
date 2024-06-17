from app import app
from flask import render_template, request, url_for, flash, redirect, session, g
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
            print(str(err))
            return 'Duplicate', -1


def execute_read_query(query):
    out = None
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
    if session['id'] is not None:
        # user_city = execute_read_query("SELECT City FROM NormalUser WHERE UserID = {}".format(session['id']))
        # ads = execute_read_query("SELECT * FROM Advertise WHERE Advertise.City = '{}' Order BY CreatedAt ".format(user_city[0][0]))
        recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID), CreatorID, UserMade, AdCatID, Title, Price, Descriptions, Subtitle, City, Street, HouseNum, CreatedAt, UpdatedAt, Images.ImagePath"
                                       " FROM divar.Advertise JOIN divar.Images ON Advertise.AdID = Images.AdID Order BY CreatedAt")
        print(recent_ads[0:10])
        return render_template('home.html', items=recent_ads[0:10])
    else:
        return redirect(url_for('index'))


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
                session['loggedin'] = True
                session['id'] = user_id

                return redirect(url_for('home'))
            else:
                flash('email or phone is duplicate.Try another')
                return redirect(url_for('sign_up'))
    else:   # GET
        return render_template("signup.html", cities=cities)


@app.route('/item/<int:adv_id>')
def advertise_detail(adv_id):
    # advertise = next((advertise for advertise in advertises if advertise['id'] == adv_id), None)
    advertise = execute_read_query("SELECT * FROM Advertise WHERE AdID={}".format(adv_id))
    advertise_images = execute_read_query("SELECT * FROM Images WHERE AdID={}".format(adv_id))
    print(advertise_images)
    advertise_images = images_path_handler(advertise_images)
    print(advertise)
    print(advertise_images)
    if advertise is None:
        return "Item not found", 404
    return render_template('ads_detail.html', item=advertise[0], ad_images=advertise_images)


@app.route("/registerAd/", methods=['GET', 'POST'])
def register_ad():
    if session['id'] is not None:
        categories = execute_read_query("SELECT * FROM AdCat")
        cities = execute_read_query("SELECT City FROM Region")
        add_advrs = ("INSERT INTO Advertise"
                    "(CreatorID, UserMade, AdCatID, Title, Price, Descriptions, Subtitle, City, Street, HouseNum, CreatedAt, UpdatedAt) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        if request.method == 'POST':
            ad_title = handle_null_str(request.form['adTitle'])
            ad_Subtitle = handle_null_str(request.form['adSubTitle'])
            ad_Desc = handle_null_str(request.form['adDesc'])
            ad_price = handle_null_int(request.form['adPrice'])
            ad_image = handle_null_str(request.form['adImage'])
            ad_cat = handle_null_str(request.form['adCat'])
            ad_city = handle_null_str(request.form['adCity'])
            ad_street = handle_null_str(request.form['adStreet'])
            ad_houseNum = handle_null_str(request.form['adHouseNum'])
            print(ad_cat)

            data_n_ad= (session['id'],True , ad_cat, ad_title, ad_price, ad_Desc, ad_Subtitle, ad_city, ad_street,
                           ad_houseNum, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


            # Check all invalid and incomplete user data
            if not ad_title:
                flash("Please enter Title")
                return redirect(url_for('register_ad'))
            elif not ad_price:
                flash('Please enter the Price')
                return redirect(url_for('register_ad'))
            elif ad_street is None and ad_houseNum is not None:
                flash('Please enter street name!')
                return redirect(url_for('register_ad'))
            else:
                print()
                ad_insertion, ad_id = execute_insert_query(add_advrs, data_n_ad)
                if user_insertion == 'Done':
                    # session['loggedin'] = True
                    # session['id'] = user_id
                    return redirect(url_for('home'))
                else:
                    flash('email or phone is duplicate.Try another')
                    return redirect(url_for('sign_up'))
        else:  # GET
            return render_template("registerAd.html", cities=cities, categories=categories)
    else:
        return redirect(url_for('index'))
#
# @app.route("/update/", methods=['GET', 'POST'])
# def update_profile():
#