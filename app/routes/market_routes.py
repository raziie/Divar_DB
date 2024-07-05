from flask import render_template, request, url_for, flash, redirect, session, jsonify, Blueprint
import datetime
from app.input_handler import *
from app.mysql_db import *

market = Blueprint('market', __name__)


@market.route("/")
def index():
    return 'index page', 200


# TODO: didn't change to rest
@market.route("/home/", methods=['GET', 'POST'])
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
        data = { 'items': items_on_page}
        sending = {'data':data,'total_pages':total_pages,'page':page}
        print(recent_ads)
        if data is None:
            return "Nothing Found",404
        return jsonify(sending),200
        # return render_template('home.html', items=items_on_page, total_pages=total_pages, page=page)
        return sending,200
    else:
        return 'please sign up first', 401


@market.route("/registerBusiness/", methods=['GET', 'POST'])
def register_bus():
    if 'logged_in' in session:
        if request.method == 'POST':
            add_business = ("INSERT INTO Business (UserID, IsActive, BusName,"
                            " BusCatID, City, Street, HouseNum) VALUES (%s, %s, %s, %s, %s, %s, %s)")

            bus_name = handle_null_str(request.form['busName'])
            bus_cat = handle_null_int(request.form['busCat'])
            bus_city = handle_null_str(request.form['busCity'])
            bus_street = handle_null_str(request.form['busStreet'])
            bus_house_num = handle_null_int(request.form['busHouseNum'])
            data_n_business = (session['user'], True, bus_name, bus_cat, bus_city, bus_street, bus_house_num)

            # Check all invalid and incomplete user data
            if not bus_name:
                return 'Please Enter your Business Name', 400
            elif bus_street is None and bus_house_num is not None:
                return 'you entered house number.Please enter street name', 400
            else:
                bus_insertion, bus_id = execute_insert_query(add_business, data_n_business)
                if bus_insertion == 'Done':
                    return jsonify(request.form), 201
                else:
                    return bus_insertion, 401
        else:  # GET
            categories = execute_read_query("SELECT * FROM BusCat", True)
            cities = execute_read_query("SELECT City FROM Region", True)
            data = {'categories': categories, 'cities': cities}
            return jsonify(data), 200
    else:
        return 'please sign up first', 401
