from flask import session, jsonify, Blueprint,request
import datetime
from app.input_handler import *
from app.mysql_db import *

admin = Blueprint('admin', __name__)



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
        return 'Login first', 401


# TODO: incomplete
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
        return 'Login first', 401


@admin.route('/deactivate_user/<int:adv_id>', methods=['PUT'])
def deactive_user(adv_id):
    if 'logged_in' in session and session['admin']:
        user_id =execute_read_query("SELECT Advertise.CreatorID FROM divar.Advertise WHERE Advertise.AdID={}".format(adv_id),False)
        # print("usereeeeee",user_id)
        report = execute_update_query("UPDATE NormalUser SET IsActive = {} WHERE UserID= {}".format(False, user_id["CreatorID"]))
        # print("whar??",report)
        if report=='Done':
            return 'Deactivate the User',204
        else:
            return 'Something Is Wrong',400
    elif 'logged_in' in session and not session['admin']:
        return 'You are not allowed', 403
    else:
        return 'Login first', 401

@admin.route('/check_ad/<int:adv_id>', methods=['PUT'])
def check_ad(adv_id):
    if 'logged_in' in session and session['admin'] and request.method == 'PUT':
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
            return 'Checked',204
        else:
            return 'Something Is Wrong',400
    elif 'logged_in' in session and not session['admin']:
        return 'You are not allowed', 403
    else:
        return 'Login first', 401