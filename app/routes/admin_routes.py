from flask import session, jsonify, Blueprint
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


@admin.route('/delete_ad/<int:adv_id>', methods=['DELETE'])
def delete_advertise(adv_id):
    if 'logged_in' in session and session['admin']:
        print(adv_id)
        # AdID
        # StatusComment
        # UpdatedAt
        # statID
        #

        # ModifyStatus: (AUserID, AdID, CreatedAt, CreatedAt)

        "UPDATE NormalUser SET {} = '{}' WHERE UserID= {}".format(attr_name, attribute, session['user'])
        reports = execute_read_query("UPDATE Advertise "
                                     "FROM divar.AdReport JOIN divar.RepCat ON RepCat.RepCatID = AdReport.RepCatID "
                                     "WHERE AdReport.AdID = {}".format(adv_id), True)
        if len(reports) == 0:
            return 'No report to show', 404
        return jsonify(reports), 204

    elif 'logged_in' in session and not session['admin']:
        return 'You are not allowed', 403
    else:
        return 'Login first', 401

