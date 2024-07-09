from flask import render_template, request, url_for, flash, redirect, session, Blueprint
from app.input_handler import *
from app.mysql_db import *

profile = Blueprint('profile', __name__)
# This file is completely checked by M


def user_update_query(attribute, attr_name, user_type):
    if isinstance(attribute, str):
        query_format = "UPDATE " + user_type + " SET {} = '{}' WHERE UserID= {}"
        query = query_format.format(attr_name, attribute, session['user'])
    else:
        query_format = "UPDATE " + user_type + " SET {} = {} WHERE UserID= {}"
        query = query_format.format(attr_name, attribute, session['user'])
    print('query', query)
    updating = execute_update_query(query)
    if updating == 'Duplicate':
        flash('Something was duplicate. Try agin'.format(attr_name))
        return '{} is duplicate.Try agin'.format(attr_name)
    elif updating == 'Error':
        flash('Updating was incomplete. Try agin'.format(attr_name))
        return updating
    else:
        return updating


# TODO: not checked for admin user but the required code is written
@profile.route("/updateProfile/", methods=['GET', 'POST'])
def update_profile():
    if 'logged_in' in session:
        user_type = 'NormalUser'
        if session['admin']:
            user_type = 'AdminUser'
        cities = execute_read_query("SELECT City FROM Region", True)
        current_user = execute_read_query("SELECT FirstName, LastName, Email, Phone, City, Street,"
                                          " House_num FROM " + user_type + " WHERE UserID = {}"
                                          .format(session['user']), False)

        print(current_user)
        if request.method == 'POST':
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
                    flash("Invalid Email")
                    return redirect(url_for('profile.update_profile'))
                else:
                    if user_update_query(prof_email, 'Email', user_type) != 'Done':
                        return redirect(url_for('profile.update_profile'))

            # Check phone first
            if prof_phone:
                if not phone_checker(prof_phone):
                    flash("Invalid Phone Number")
                    return redirect(url_for('profile.update_profile'))
                else:
                    if user_update_query(prof_phone, 'Phone', user_type) != 'Done':
                        return redirect(url_for('profile.update_profile'))

            prof = (prof_f_name, prof_l_name, prof_city, prof_street, prof_house_num)
            print('profile', prof)
            names = ('FirstName', 'LastName', 'City', 'Street', 'House_num')
            for i in range(len(prof)):
                if prof[i] is not None and current_user[names[i]] != prof[i]:
                    print(prof[i])
                    if user_update_query(prof[i], names[i], user_type) != 'Done':
                        return redirect(url_for('profile.update_profile'))

            return redirect(url_for('market.home'))

        else:  # GET
            return render_template("profile/updateProfile.html", cities=cities, curr=current_user)
    else:
        flash('Please sign up or login first')
        return redirect(url_for('market.index'))
