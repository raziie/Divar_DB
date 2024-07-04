from flask import render_template, request, url_for, flash, redirect, session, jsonify, Blueprint
import datetime
from app.input_handler import *
from app.mysql_db import *

ad = Blueprint('ad', __name__)


@ad.route('/detail/<int:adv_id>')
def advertise_detail(adv_id):
    if 'logged_in' in session:
        execute_insert_query("INSERT INTO Visit (AdID, UserID) VALUES (%s, %s)", (adv_id, session['user']))
        advertise = execute_read_query("SELECT * FROM Advertise WHERE AdID={}".format(adv_id), False)
        advertise_images = execute_read_query("SELECT * FROM Images WHERE AdID={}".format(adv_id), True)
        advertise_images = images_path_handler(advertise_images)
        advertise['images'] = advertise_images
        if advertise is None:
            return 'advertise not found', 404
        return jsonify(advertise), 200
    else:
        return 'please sign up first', 401


@ad.route("/registerAd/", methods=['GET', 'POST'])
def register_ad():
    if 'logged_in' in session:
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
            print(session['user'])
            data_n_ad = (session['user'], True, ad_cat, ad_title, ad_price, ad_description, ad_subtitle, ad_city,
                         ad_street, ad_house_num, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Check all invalid and incomplete user data
            if not ad_title:
                return 'Please enter Title', 400
            elif not ad_price:
                return 'Please enter the Price', 400
            elif ad_street is None and ad_house_num is not None:
                return 'you have entered house number.Please enter street name too', 400
            else:
                ad_insertion, ad_id = execute_insert_query(add_advertise, data_n_ad)
                if ad_insertion == 'Done':
                    return jsonify(request.form), 201
                elif "Column 'AdCatID' cannot be null" in ad_insertion:
                    return 'please select category', 401
                elif "Column 'Price' cannot be null" in ad_insertion:
                    return 'please select category', 401
                else:
                    return ad_insertion, 401
        else:  # GET
            categories = execute_read_query("SELECT * FROM AdCat", True)
            cities = execute_read_query("SELECT City FROM Region", True)
            data = {'cities': cities, 'categories': categories}
            return jsonify(data), 200
    else:
        return 'please sign up first', 401


@ad.route("/reportAd/<int:ad_id>", methods=['GET', 'POST'])
def report_ad(ad_id):
    if 'logged_in' in session:
        if request.method == 'POST':
            add_report = ("INSERT INTO AdReport (AdID, UserID, RepCatID, Content) "
                          "VALUES (%s, %s, %s, %s)")
            rep_cat = handle_null_int(request.form['repCat'])
            rep_content = handle_null_str(request.form['repContent'])

            data_n_report = (ad_id, session['user'], rep_cat, rep_content)
            report_insertion, _ = execute_insert_query(add_report, data_n_report)
            if report_insertion == 'Done':
                return jsonify(request.form), 201
            elif "foreign key constraint" in report_insertion:
                return 'advertise not found', 404
            else:
                return report_insertion
        else:  # GET
            categories = execute_read_query("SELECT * FROM RepCat", True)
            return jsonify(categories), 200
    else:
        return 'please sign up first', 401


# incomplete
@ad.route("/advertiseStatus/")
def advertise_status():
    if 'logged_in' in session:
        # TODO : Complete the query to have status or handle in back or front to have type of status
        ads = execute_read_query("SELECT AdID, Title, Price, Descriptions, Subtitle, City, Street, HouseNum,"
                                 "CreatedAt, StatusComment, statID FROM divar.AdStatus JOIN divar.Advertise on "
                                 "AdStatus.AdID = Advertise.AdID WHERE UserID = {}"
                                 .format(session['user']), False)

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
