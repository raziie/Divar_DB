from flask import render_template, request, url_for, flash, redirect, session, Blueprint
from app.input_handler import *
from app.mysql_db import *
from app.elastic_helper import ElasticSearchDB

elastic_client = ElasticSearchDB()
market = Blueprint('market', __name__)
prev_page = 0

def re_order_list(cat_id, cats):
    the_cat = {}
    the_cat_index = 0
    for t in range(len(cats)):
        if cats[t]['AdCatID'] == cat_id:
            the_cat_index = t
            break
    the_cat = cats[the_cat_index]
    cats.pop(the_cat_index)
    cats.insert(0, the_cat)
    return cats


# checked by m
@market.route("/")
def index():
    return render_template("market/index.html")


@market.route("/home/", methods=['GET', 'POST'])
def home():
    global elastic_client, last_search, prev_page
    if 'logged_in' in session and not session['admin']:
        categories = execute_read_query("SELECT * FROM AdCat", True)

        categories.insert(0, {'AdCatID': -1, 'Category': 'all'})
        print('fffffffffffffffffffff')
        form_data = {'page': 1, 'searchString': '', 'adCat': -1, 'minPrice': 0, 'maxPrice': 1000000000, 'photo': ''}
        if request.method == 'GET':
            page = 1
            recent_ads = elastic_client.search_query(searched_str='', category=-1,
                                                     price_range=(None, None), photo='', is_admin=False)

        elif request.method == 'POST':
            page = handle_null_int(request.form['page'])
            print('form page:', page)
            searched = str(request.form['searchString'])
            ads_category = handle_null_int(request.form['adCat'])
            ads_price_min = handle_null_float(request.form['minPrice'])
            ads_price_max = handle_null_float(request.form['maxPrice'])
            ads_photo = ''
            if 'photo' in request.form.keys():
                ads_photo = handle_null_str(request.form['photo'])

            if ads_category != -1:
                categories = re_order_list(ads_category, categories)
            form_data = request.form
            print(ads_category, (ads_price_min, ads_price_max), ads_photo)
            recent_ads = elastic_client.search_query(searched_str=searched, category=ads_category,
                                                     price_range=(ads_price_min, ads_price_max),
                                                     photo=ads_photo, is_admin=False)

            print('recent ads in form:\n', recent_ads)



        per_page = 12
        start = (page - 1) * per_page
        end = start + per_page
        print(recent_ads)
        total_pages = (len(recent_ads) + per_page - 1) // per_page
        items_on_page = recent_ads[start:end]
        # print(recent_ads)

        if items_on_page is None:
            flash('Nothing Found')
            print('555ff', page)
            prev_page = page
            return render_template('market/home.html', items=None, total_pages=1,
                               page=1, ad_categories=categories, form_data=form_data)

        if page != prev_page:
            prev_page = page
            print('1fff', page)
            return render_template('market/home.html', items=items_on_page, total_pages=total_pages,
                                   page=page, ad_categories=categories, form_data=form_data)

        print('fudd', page)
        prev_page = page
        return render_template('market/home.html', items=items_on_page, total_pages=total_pages,
                               page=page, ad_categories=categories, form_data=form_data)

    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))


# changed but has bug
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
                flash('Please Enter your Business Name')
                return redirect(url_for('market.register_bus'))
            elif bus_street is None and bus_house_num is not None:
                flash('You Entered House Number.Please Enter Street Name')
                return redirect(url_for('market.register_bus'))
            else:
                bus_insertion, bus_id = execute_insert_query(add_business, data_n_business)
                if bus_insertion == 'Done':
                    return redirect(url_for('market.home'))
                else:
                    flash('Business Name is duplicate.Try another')
                    return redirect(url_for('register_bus'))
        else:  # GET
            categories = execute_read_query("SELECT * FROM BusCat", True)
            cities = execute_read_query("SELECT City FROM Region", True)
            data = {'categories': categories, 'cities': cities}
            return render_template("market/registerBus.html", cities=cities, categories=categories)
    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))
