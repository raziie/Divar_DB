from flask import session, jsonify, Blueprint,request
import datetime
from app.input_handler import *
from app.mysql_db import *

admin = Blueprint('admin', __name__)

@market.route("/admin_home/", methods=['GET', 'POST'])
def admin_home():
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
            # return "Nothing Found",404
            flash('Nothing Found')
            return redirect(url_for('admin.admin_home'))
        # return jsonify(sending),200
        return render_template('admin_home.html', items=items_on_page, total_pages=total_pages, page=page)
        # return sending,200
    else:
        flash('Please Sign up First')
        return redirect(url_for('market.index'))
        # return 'please sign up first', 401


#TODO: ADD HTML AND CHANGE TO TEMPLATE RENDER
@admin.route('/get_reports/<int:adv_id>', methods=['GET'])
def get_reports(adv_id):
    if 'logged_in' in session and session['admin']:
        print(adv_id)
        reports = execute_read_query("SELECT AdReport.ReportNum, AdReport.UserID, AdReport.Content, RepCat.Category "
                                     "FROM divar.AdReport JOIN divar.RepCat ON RepCat.RepCatID = AdReport.RepCatID "
                                     "WHERE AdReport.AdID = {}".format(adv_id), True)
        if len(reports) == 0:
            return 'No report to show', 404
        return jsonify(reports), 200
    elif 'logged_in' in session and not session['admin']:
        return 'You are not allowed', 403
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
        if modify_status_insertion=='Done' and status_insertion == 'Done':
            return 'Deleted',204
        else:
            return 'Something Is Wrong',400
    elif 'logged_in' in session and not session['admin']:
        return 'You are not allowed', 403
    else:
        flash('Please Log in First')
        return redirect(url_for('market.index'))


@admin.route('/deactivate_user/<int:adv_id>', methods=['PUT'])
def deactive_user(adv_id):
    if 'logged_in' in session and session['admin']:
        user_id =execute_read_query("SELECT Advertise.CreatorID FROM divar.Advertise WHERE Advertise.AdID={}".format(adv_id),False)
        # print("usereeeeee",user_id)
        report = execute_update_query("UPDATE NormalUser SET IsActive = {} WHERE UserID= {}".format(False, user_id["CreatorID"]))
        # print("whar??",report)
        if report=='Done':
            # return 'Deactivate the User',204
            flash('Deactivated the User')
            return redirect(url_for('market.home'))
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

@admin.route('/check_ad/<int:adv_id>', methods=['POST, GET'])
def check_ad(adv_id):
    if 'logged_in' in session and session['admin'] and request.method == 'PUT':
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
                return redirect(url_for('admin.admin_home'))
            else:
                # return 'Something Is Wrong',400
                flash('Something Is Wrong')
                return redirect(url_for('admin.admin_home'))
        else:  # GET
            categories = execute_read_query("SELECT * FROM RepCat", True)
            # return jsonify(categories), 200
            return render_template("check_ad.html", AdID=ad_id)
    elif 'logged_in' in session and not session['admin']:
        # return 'You are not allowed', 403
        flash('You are not allowed')
        return redirect(url_for('admin.admin_home'))
    else:
        flash('Please Log in First')
        return redirect(url_for('admin.admin_home'))