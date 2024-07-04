from flask import render_template, request, url_for, flash, redirect, session, jsonify, Blueprint
import datetime
from app.input_handler import *
from app.mysql_db import *

profile = Blueprint('profile', __name__)


def user_update_query(attribute, attr_name):
    if isinstance(attribute, str):
        query = "UPDATE NormalUser SET {} = '{}' WHERE UserID= {}".format(attr_name, attribute, session['user'])
    else:
        query = "UPDATE NormalUser SET {} = {} WHERE UserID= {}".format(attr_name, attribute, session['user'])
    print('query', query)
    updating = execute_update_query(query)
    if updating == 'Duplicate':
        return '{} is duplicate.Try agin'.format(attr_name)
    elif updating == 'Error':
        # flash('Updating was incomplete. Try agin'.format(attr_name))
        return updating
    else:
        return updating


@profile.route("/updateProfile/", methods=['GET', 'PUT'])
def update_profile():
    if 'logged_in' in session:
        cities = execute_read_query("SELECT City FROM Region", True)
        current_user = execute_read_query("SELECT FirstName, LastName, Email, Phone, City, Street,"
                                          " House_num FROM NormalUser WHERE UserID = {}"
                                          .format(session['user']), False)
        if request.method == 'PUT':
            prof_f_name = handle_null_str(request.form['inFName'])
            prof_l_name = handle_null_str(request.form['inLName'])
            prof_phone = handle_null_str(request.form['inPhone'])
            prof_email = handle_null_str(request.form['inEmail'])
            prof_city = handle_null_str(request.form['uCity'])
            prof_street = handle_null_str(request.form['inStreet'])
            prof_house_num = handle_null_int(request.form['inHouseNum'])

            # Check email first
            if prof_email:
                if not email_checker(prof_email):
                    return "Invalid Email", 401
                else:
                    if user_update_query(prof_email, 'Email') != 'Done':
                        return redirect(url_for('update_profile'))
            # Check phone first
            if prof_phone:
                if not phone_checker(prof_phone):
                    flash("Invalid Phone Number")
                    return redirect(url_for('update_profile'))
                else:
                    if user_update_query(prof_phone, 'Phone') != 'Done':
                        return redirect(url_for('update_profile'))

            prof = (prof_f_name, prof_l_name, prof_city, prof_street, prof_house_num)
            print('profile', prof)
            names = ('FirstName', 'LastName', 'City', 'Street', 'House_num')
            for i in range(len(prof)):
                if prof[i] is not None and current_user[names[i]] != prof[i]:
                    print(prof[i])
                    if user_update_query(prof[i], names[i]) != 'Done':
                        return redirect(url_for('update_profile'))

            return redirect(url_for('home'))

        else:  # GET
            data = {'cities': cities, 'current user':current_user}
            return jsonify(data), 200
    else:
        return 'please sign up first', 401
