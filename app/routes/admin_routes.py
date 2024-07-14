from flask import render_template, request, url_for, redirect, session, jsonify, Blueprint,request, flash
import datetime
from app.input_handler import *
from app.mysql_db import *
from app.routes.market_routes import elastic_client
admin = Blueprint('admin', __name__)


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


@admin.route("/admin_home/", methods=['GET', 'POST'])
def admin_home():
    global elastic_client, last_search, prev_page
    if 'logged_in' in session and session['admin']:
        categories = execute_read_query("SELECT * FROM AdCat", True)

        categories.insert(0, {'AdCatID': -1, 'Category': 'all'})
        print('fffffffffffffffffffff')
        form_data = {'page': 1, 'searchString': '', 'adCat': -1, 'minPrice': 0, 'maxPrice': 1000000000, 'photo': ''}
        if request.method == 'GET':
            page = 1
            recent_ads = elastic_client.search_query(searched_str='', category=-1,
                                                     price_range=(None, None), photo='', is_admin=True)

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
                                                     photo=ads_photo, is_admin=True)

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
            return render_template('admin_home.html', items=None, total_pages=1,
                                   page=1, ad_categories=categories, form_data=form_data)

        if page != prev_page:
            prev_page = page
            print('1fff', page)
            return render_template('admin_home.html', items=items_on_page, total_pages=total_pages,
                                   page=page, ad_categories=categories, form_data=form_data)

        print('fudd', page)
        prev_page = page
        return render_template('admin_home.html', items=items_on_page, total_pages=total_pages,
                               page=page, ad_categories=categories, form_data=form_data)

    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))

    # if 'logged_in' in session:
    #     recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID), AdCatID, Title,"
    #                                     "Price, Descriptions, Subtitle, City, Street, HouseNum, CreatedAt"
    #                                     " ,Images.ImagePath FROM divar.Advertise LEFT JOIN divar.Images "
    #                                     "ON Advertise.AdID = Images.AdID Order BY CreatedAt DESC", True)
    #
    #     if request.method == 'POST':
    #         searched = str(request.form['searchString'])
    #         print(searched)
    #         recent_ads = execute_read_query("SELECT DISTINCT(Advertise.AdID), AdCatID, Title, Price, "
    #                                         "Descriptions, Subtitle, City, Street, HouseNum, CreatedAt,"
    #                                         "Images.ImagePath  FROM divar.Advertise LEFT JOIN divar.Images "
    #                                         "ON Advertise.AdID = Images.AdID "
    #                                         "WHERE Advertise.Title LIKE '%{}%'"
    #                                         "Order BY CreatedAt DESC".format(searched), True)
    #
    #     for i in range(len(recent_ads)):
    #         delta = datetime.datetime.now() - recent_ads[i]['CreatedAt']
    #         recent_ads[i]['DaysPast'] = delta.days
    #
    #
    #     page = request.args.get('page', 1, type=int)
    #     per_page = 12
    #     start = (page - 1) * per_page
    #     end = start + per_page
    #     total_pages = (len(recent_ads) + per_page - 1) // per_page
    #     items_on_page = recent_ads[start:end]
    #     data = { 'items': items_on_page}
    #     sending = {'data':data,'total_pages':total_pages,'page':page}
    #     print(recent_ads)
    #     if data is None:
    #         # return "Nothing Found",404
    #         flash('Nothing Found')
    #         return redirect(url_for('admin.admin_home'))
    #     # return jsonify(sending),200
    #     return render_template('admin_home.html', items=items_on_page, total_pages=total_pages, page=page)
    #     # return sending,200
    # else:
    #     flash('Please Sign up First')
    #     return redirect(url_for('market.index'))
    #     # return 'please sign up first', 401


@admin.route('/admin_ad/<int:adv_id>', methods=['GET'])
def admin_ad(adv_id):
    if 'logged_in' in session and session['admin']:
        # execute_insert_query("INSERT INTO Visit (AdID, UserID) VALUES (%s, %s)", (adv_id, session['user']))
        advertise = execute_read_query("SELECT * FROM Advertise WHERE AdID={}".format(adv_id), False)
        advertise_images = execute_read_query("SELECT * FROM Images WHERE AdID={}".format(adv_id), True)
        advertise_images = images_path_handler(advertise_images)
        advertise['images'] = advertise_images
        if advertise is None:
            flash('Advertise not Found')
            return redirect(url_for('admin_home.html'))

        return render_template('admin_ad.html', item=advertise, ad_images=advertise_images)
    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))


@admin.route('/get_reports/<int:adv_id>', methods=['GET'])
def get_reports(adv_id):
    if 'logged_in' in session and session['admin']:
        print(adv_id)
        reports = execute_read_query("SELECT AdReport.ReportNum, AdReport.UserID, AdReport.Content, RepCat.Category "
                                     "FROM divar.AdReport JOIN divar.RepCat ON RepCat.RepCatID = AdReport.RepCatID "
                                     "WHERE AdReport.AdID = {}".format(adv_id), True)
        print(reports)
        creator_id = execute_read_query("SELECT Advertise.CreatorID, Advertise.UserMade "
                                        "FROM divar.Advertise "
                                        "WHERE Advertise.AdID = {}".format(adv_id), False)
        print(creator_id)
        if creator_id['UserMade']:
            creator_name = execute_read_query("SELECT NormalUser.FirstName, NormalUser.LastName "
                                               "FROM divar.NormalUser "
                                               "WHERE NormalUser.UserID = {}".format(creator_id['CreatorID']), False)
            creator_name = creator_name['FirstName']+" "+creator_name['LastName']
        else:
            creator_name = execute_read_query("SELECT Business.BusName "
                                              "FROM divar.Business "
                                              "WHERE Business.UserID = {}".format(creator_id['CreatorID']), False)
            print(creator_name)
            creator_name = creator_name['BusName']
        # print(creator_name)
        for i in range(len(reports)):
            rep = reports[i]
            # print("ad",advertise)
            # print(advertise["AdID"])
            user_name = execute_read_query("SELECT NormalUser.FirstName, NormalUser.LastName "
                                           "FROM divar.AdReport JOIN divar.NormalUser ON AdReport.UserID = NormalUser.UserID "
                                           "WHERE AdReport.ReportNum = {}".format(rep["ReportNum"]), True)
            # print("user name", user_name[0])
            # print(type(user_name[0]))
            reports[i]['user_firstname'] = user_name[0]['FirstName']
            reports[i]['user_lastname'] = user_name[0]['LastName']
            if not reports[i]['Content'] :
                reports[i]['Content'] = " "
        # print(reports)
        # print(user_name)
        print(creator_name)
        # if len(reports) == 0:
        #     # return 'No report to show', 404
        #     flash('No report to show')
        #     return redirect(url_for('admin.admin_home'))
        # return jsonify(reports), 200
        return render_template("admin_reports.html", items=reports, AdID=adv_id, creator=creator_name)
    elif 'logged_in' in session and not session['admin']:
        # return 'You are not allowed', 403
        flash('You are not allowed')
        return redirect(url_for('admin.admin_home'))
    else:
        flash('Please Log in First')
        return redirect(url_for('market.index'))


# TODO: incomplete
# handeled in check_ad
@admin.route('/delete_ad/<int:adv_id>', methods=['PUT'])
def delete_advertise(adv_id):
    if 'logged_in' in session and session['admin'] and request.method == 'PUT':
        print(adv_id)
        comment = handle_null_str(request.form['comment'])
        add_satus = ("UPDATE AdStatus SET StatusComment='{}', UpdatedAt='{}', statID={} WHERE AdID={}"
                     .format(comment, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, adv_id))
        status_insertion = execute_update_query(add_satus)
        add_modify_satus = ("INSERT INTO ModifyStatus"
                    "(AUserID, AdID, CreatedAt, statID) "
                    "VALUES (%s, %s, %s, %s)")
        data_modify = (session['user'], adv_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0)
        modify_status_insertion, status_id= execute_insert_query(add_modify_satus,data_modify)
        # print("s",modify_status_insertion[1])
        # print("q",status_insertion)
        # print("avali",modify_status_insertion=='Done')
        # print("dovomi",status_insertion == 'Done')
        # print("here",( modify_status_insertion=='Done' and status_insertion == 'Done'))
        if modify_status_insertion == 'Done' and status_insertion == 'Done':
            # return 'Deleted',204
            print("deleted the ad", adv_id)
            flash('Deleted the Advertise')
            return redirect(url_for('admin.admin_home'))
        else:
            # return 'Something Is Wrong',400
            flash('Something Is Wrong')
            return redirect(url_for('admin.admin_home'))
    elif 'logged_in' in session and not session['admin']:
        # return 'You are not allowed', 403
        flash('You are not allowed')
        return redirect(url_for('admin.admin_home'))
    else:
        flash('Please Log in First')
        return redirect(url_for('market.index'))


@admin.route('/deactivate_user/<int:adv_id>', methods=['GET'])
def deactive_user(adv_id):
    if 'logged_in' in session and session['admin']:
        report_other_ads = 'Done'
        creator =execute_read_query("SELECT Advertise.CreatorID, Advertise.UserMade FROM divar.Advertise WHERE Advertise.AdID={}".format(adv_id), False)
        # print(creator)
        if creator['UserMade']:
            report = execute_update_query("UPDATE NormalUser SET IsActive = {} WHERE UserID= {}".format(False, creator["CreatorID"]))
            ads =  execute_read_query("SELECT Advertise.AdID FROM Advertise WHERE Advertise.CreatorID={}".format(creator["CreatorID"]), True)
            for i in range(len(ads)):
                report_other_ads = execute_update_query(
                    "UPDATE divar.Advertise JOIN divar.AdStatus ON AdStatus.AdID = Advertise.AdID SET statID = 0 WHERE Advertise.AdID= {}".format(ads[i]['AdID']))
        else:
            report = execute_update_query("UPDATE Business SET IsActive = {} WHERE UserID= {}".format(False, creator["CreatorID"]))
            ads = execute_read_query(
                "SELECT Advertise.AdID FROM Advertise WHERE Advertise.CreatorID={} AND UserMade=TRUE".format(creator["CreatorID"]),
                True)
            for i in range(len(ads)):
                report_other_ads = execute_update_query(
                    "UPDATE Advertise JOIN AdStatus ON AdStatus.AdID = Advertise.AdID SET statID = 0 WHERE AdID= {} AND UserMade=FALSE".format(
                        ads[i]['AdID']))
        # print("whar??",report)
        if report=='Done' and report_other_ads=='Done':
            # return 'Deactivate the User',204
            print("deaciveted the user",creator["CreatorID"])
            flash('Deactivated the User')
            return redirect(url_for('admin.admin_home'))
        else:
            # return 'Something Is Wrong',400
            flash('Something Is Wrong')
            return redirect(url_for('admin.admin_home'))
    elif 'logged_in' in session and not session['admin']:
        # return 'You are not allowed', 403
        flash('You are not allowed')
        return redirect(url_for('admin.admin_home'))
    else:
        flash('Please Log in First')
        return redirect(url_for('market.index'))

@admin.route('/check_ad/<int:adv_id>', methods=['GET', 'POST'])
def check_ad(adv_id):
    # print('logged_in' in session and session['admin'])
    if 'logged_in' in session and session['admin']:
        if request.method == 'POST':
            print(adv_id)
            comment = handle_null_str(request.form['comment'])
            statID = handle_null_int(request.form['statID'])
            add_satus = ("UPDATE AdStatus SET StatusComment='{}', UpdatedAt='{}', statID={} WHERE AdID={}"
                         .format(comment, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), statID, adv_id))
            status_insertion = execute_update_query(add_satus)
            add_modify_satus = ("INSERT INTO ModifyStatus"
                                "(AUserID, AdID, CreatedAt, statID) "
                                "VALUES (%s, %s, %s, %s)")
            data_modify = (session['user'], adv_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), statID)
            modify_status_insertion, status_id = execute_insert_query(add_modify_satus, data_modify)

            if modify_status_insertion=='Done' and status_insertion == 'Done':
                # return 'Checked',204
                flash('Status Changed')
                return redirect(url_for('admin.admin_home'))
            else:
                # return 'Something Is Wrong',400
                flash('Something Is Wrong')
                return redirect(url_for('admin.admin_home'))
        else:  # GET
            categories = execute_read_query("SELECT * FROM RepCat", True)
            # return jsonify(categories), 200
            return render_template("check_ad.html", AdID = adv_id)
    elif 'logged_in' in session and not session['admin']:
        # return 'You are not allowed', 403
        flash('You are not allowed')
        return redirect(url_for('admin.admin_home'))
    else:
        flash('Please Log in First')
        return redirect(url_for('market.index'))