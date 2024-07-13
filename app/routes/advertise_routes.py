from flask import render_template, request, url_for, flash, redirect, session, jsonify, Blueprint
import datetime
from app.input_handler import *
from app.mysql_db import *

ad = Blueprint('ad', __name__)


# checked by m
@ad.route('/detail/<int:adv_id>', methods=['GET'])
def advertise_detail(adv_id):
    if 'logged_in' in session and not session['admin']:
        execute_insert_query("INSERT INTO Visit (AdID, UserID) VALUES (%s, %s)", (adv_id, session['user']))
        advertise = execute_read_query("SELECT * FROM Advertise WHERE AdID={}".format(adv_id), False)
        advertise_images = execute_read_query("SELECT * FROM Images WHERE AdID={}".format(adv_id), True)
        advertise_images = images_path_handler(advertise_images)
        advertise['images'] = advertise_images
        if advertise is None:
            flash('Advertise not Found')
            return redirect(url_for('market.home.html'))

        return render_template('ads_detail.html', item=advertise, ad_images=advertise_images)
    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))


# checked
@ad.route("/registerAd/", methods=['GET', 'POST'])
def register_ad():
    if 'logged_in' in session and not session['admin']:
        add_advertise = ("INSERT INTO Advertise (CreatorID, UserMade, AdCatID, Title, Price, Descriptions,"
                         " Subtitle, City, Street, HouseNum, CreatedAt, UpdatedAt) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        add_status = ("INSERT INTO AdStatus (AdID, StatusComment, UpdatedAt, statID)"
                         "VALUES (%s, %s, %s, %s)")
        # TODO: NOT CHECKED
        businesses = execute_read_query("SELECT * FROM Business WHERE UserID = {}".format(session['user']), True)
        print("business", businesses)

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
                # return 'Please enter Title', 400
                flash("Please enter Title")
                return redirect(url_for('ad.register_ad'))
            elif not ad_price:
                # return 'Please enter the Price', 400
                flash('Please enter the Price')
                return redirect(url_for('ad.register_ad'))
            elif ad_street is None and ad_house_num is not None:
                # return 'you have entered house number.Please enter street name too', 400
                flash('Please enter street name!')
                return redirect(url_for('ad.register_ad'))
            else:
                ad_insertion, ad_id = execute_insert_query(add_advertise, data_n_ad)
                data_status = (ad_id, " ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 3)
                status_insertion, status_id = execute_insert_query(add_status, data_status)
                print("a", ad_insertion)
                print("b", status_insertion)
                # TODO: IT HAS "Not all parameters were used in the SQL statement" ERROR FOR status_insertion
                if ad_insertion == 'Done' and status_insertion == 'Done':
                    # return jsonify(request.form), 201
                    return redirect(url_for('market.home'))
                elif "Column 'AdCatID' cannot be null" in ad_insertion:
                    # return 'please select category', 401
                    flash('Please Select Category for Advertise Category')
                    return redirect(url_for('ad.register_ad'))
                elif "Column 'Price' cannot be null" in ad_insertion:
                    # return 'please select category', 401
                    flash('Price can not be Null')
                    return redirect(url_for('ad.register_ad'))
                else:
                    # return ad_insertion, 401
                    flash('Something went Wrong')
                    return redirect(url_for('ad.register_ad'))
        else:  # GET
            categories = execute_read_query("SELECT * FROM AdCat", True)
            cities = execute_read_query("SELECT City FROM Region", True)
            data = {'cities': cities, 'categories': categories}
            # return jsonify(data), 200
            return render_template("registerAd.html", cities=cities, categories=categories)
    else:
        # return 'please sign up first', 401
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))


# checked by m
@ad.route("/reportAd/<int:ad_id>", methods=['GET', 'POST'])
def report_ad(ad_id):
    if 'logged_in' in session and not session['admin']:
        if request.method == 'POST':
            add_report = ("INSERT INTO AdReport (AdID, UserID, RepCatID, Content) "
                          "VALUES (%s, %s, %s, %s)")
            rep_cat = handle_null_int(request.form['repCat'])
            rep_content = handle_null_str(request.form['repContent'])

            data_n_report = (ad_id, session['user'], rep_cat, rep_content)
            report_insertion, _ = execute_insert_query(add_report, data_n_report)
            if report_insertion == 'Done':
                return redirect('http://127.0.0.1:5000/ad/detail/' + str(ad_id))
            elif "foreign key constraint" in report_insertion:
                flash('Advertise not Found')
                return redirect(url_for('market.home'))
            else:
                flash("Something went wrong.Try another")
                return redirect(url_for('ad.report_ad'))
        else:  # GET
            categories = execute_read_query("SELECT * FROM RepCat", True)
            return render_template("reportAd.html", categories=categories, AdID=ad_id)
    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))


# incomplete
@ad.route("/advertiseStatus/")
def advertise_status():
    if 'logged_in' in session:
        # TODO : Complete the query to have status or handle in back or front to have type of status
        # print("hey",session['user'])
        ads = execute_read_query("SELECT * FROM divar.AdStatus JOIN divar.Advertise on "
                                 "AdStatus.AdID = Advertise.AdID WHERE Advertise.CreatorID = {}"
                                 .format(session['user']), True)
        print(ads)
        if ads is None:
            # return 'No Advertise Found', 404
            flash('No Advertise Found')
            return redirect(url_for('market.home'))
        # dict_ads = []
        for i in range(len(ads)):
            advertise = ads[i]
            # print("ad",advertise)
            # print(advertise["AdID"])
            visit_number = execute_read_query("SELECT COUNT(UserID) FROM divar.Visit WHERE Visit.AdID = {}"
                                              .format(advertise["AdID"]), False)
            # print("visit", visit_number)
            # print(visit_number["COUNT(UserID)"])
            ads[i]['visits'] = visit_number["COUNT(UserID)"]

            status = execute_read_query("SELECT stat FROM divar.Stat WHERE Stat.statID = {}"
                                              .format(advertise['statID']), False)
            ads[i]['status'] = status['stat'].lower()

            delta = datetime.datetime.now() - ads[i]['CreatedAt']
            ads[i]['DaysPast'] = delta.days
            # method convert a list to a dictionary to better handle in html (you can see usage in user update route)
            # advertise = convert_to_dict(advertise, ('AdID', 'Title', 'Price', 'Descriptions', 'Subtitle',
            #                                         'City', 'Street', 'HouseNum', 'CreatedAt', 'StatusComment',
            #                                         'statID'), [])
            # dict_ads.append(advertise)


        # TODO: pass dict_ads to front to have complete data and also
        # TODO: (front) complete page so that each advertise be more specific and big
        # print("here",ads)

        # return jsonify(ads), 200
        return render_template('status.html', items=ads)
    else:
        # return 'please sign up first', 401
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))