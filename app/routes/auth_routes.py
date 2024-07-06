from flask import request, session, jsonify, Blueprint, render_template, url_for, flash, redirect
import datetime
from app.input_handler import *
from app.mysql_db import *
from app.utils import redis_cache
import random


auth = Blueprint('auth', __name__)


def generate_otp(length=6):
    return ''.join(random.choices('0123456789', k=length))


@auth.route('/user_request_otp/', methods=['POST'])
def user_request_otp():
    if request.method == 'POST':
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])

        user_id = execute_read_query("SELECT UserID FROM NormalUser WHERE Email= '{}'".format(in_email), False)
        if user_id is None:
            user_id = execute_read_query("SELECT UserID FROM NormalUser WHERE Phone ='{}'".format(in_phone), False)

        if user_id is None:
            return redirect(url_for('index'))

        otp = generate_otp()
        if redis_cache.exists('N'+str(user_id['UserID'])):
            redis_cache.delete('N'+str(user_id['UserID']))

        redis_cache.setex('N'+str(user_id['UserID']), 30000, otp)
        return jsonify({'otp': otp, 'user_id': user_id['UserID'], 'email': in_email, 'Phone': in_phone,
                        'message': 'OTP generated successfully'}), 200


@auth.route('/user_validate_otp/<user_id>', methods=['POST'])
def user_validate_otp(user_id):
    input_otp = handle_null_str(request.form['otp'])
    stored_otp = redis_cache.get('N' + str(user_id))

    if stored_otp is None:
        return jsonify({'message': 'OTP expired or not set'}), 400

    if input_otp == stored_otp:
        redis_cache.delete('N'+str(user_id))
        session['logged_in'] = True
        session['user'] = user_id
        session['admin'] = False
        return 'OTP validated successfully', 200
    else:
        return 'Invalid OTP', 400


@auth.route('/admin_request_otp/', methods=['POST'])
def admin_request_otp():
    if request.method == 'POST':
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])

        user_id = execute_read_query("SELECT AUserID FROM AdminUser WHERE Email= '{}'".format(in_email), False)
        if user_id is None:
            user_id = execute_read_query("SELECT AUserID FROM AdminUser WHERE Phone ='{}'".format(in_phone), False)

        if user_id is None:
            return 'you are not allowed', 401

        otp = generate_otp()
        if redis_cache.exists('A'+str(user_id['AUserID'])):
            redis_cache.delete('A'+str(user_id['AUserID']))

        redis_cache.setex('A'+str(user_id['AUserID']), 30000, otp)
        return jsonify({'otp': otp, 'user_id': user_id['AUserID'], 'email': in_email, 'Phone': in_phone,
                        'message': 'OTP generated successfully'}), 200


@auth.route('/admin_validate_otp/<user_id>', methods=['POST'])
def admin_validate_otp(user_id):
    input_otp = handle_null_str(request.form['otp'])
    stored_otp = redis_cache.get('A' + str(user_id))

    if stored_otp is None:
        return jsonify({'message': 'OTP expired or not set'}), 400

    if input_otp == stored_otp:
        redis_cache.delete('A'+str(user_id))
        session['logged_in'] = True
        session['user'] = user_id
        session['admin'] = True
        return 'OTP validated successfully', 200
    else:
        return 'Invalid OTP', 400


#changed
@auth.route("/signup/", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        add_user = ("INSERT INTO NormalUser"
                    "(IsActive, FirstName, LastName, RegisteredAt, Email, Phone, City, Street, House_num) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

        in_f_name = handle_null_str(request.form['inFName'])
        in_l_name = handle_null_str(request.form['inLName'])
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])
        in_city = handle_null_str(request.form['uCity'])
        in_street = handle_null_str(request.form['inStreet'])
        in_house_num = handle_null_int(request.form['inHouseNum'])

        data_n_user = (1, in_f_name, in_l_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), in_email,
                       in_phone, in_city, in_street, in_house_num)

        # Check all invalid and incomplete user data
        if not in_email and not in_phone:
            # return 'One of Email or Phone is required!', 401
            flash('One of Email or Phone is required!')
            return redirect(url_for('auth.sign_up'))
        elif not in_f_name or not in_l_name:
            # return 'You should enter yor name completely!', 401
            flash('You should enter yor name completely!')
            return redirect(url_for('auth.sign_up'))
        elif not email_checker(in_email):
            # return 'Invalid Email', 401
            flash('Invalid Email')
            return redirect(url_for('auth.sign_up'))
        elif not phone_checker(in_phone):
            # return 'Invalid Phone Number', 401
            flash('Invalid Phone Number')
            return redirect(url_for('auth.sign_up'))
        elif in_street is None and in_house_num is not None:
            # return 'Please enter street name!', 401
            flash('Please enter street name!')
            return redirect(url_for('auth.sign_up'))
        else:
            user_insertion, user_id = execute_insert_query(add_user, data_n_user)
            if user_insertion == 'Done':
                session['logged_in'] = True
                session['user'] = user_id
                session['admin'] = False
                print(session['user'])
                return redirect(url_for('market.home'))
            elif user_insertion == 'Duplicate':
                flash('email or phone is duplicate.Try another')
                return redirect(url_for('auth.sign_up'))
            else:
                return redirect(url_for('auth.sign_up'))
    else:   # GET
        cities = execute_read_query("SELECT City FROM Region", True)
        print(cities)
        return render_template("signup.html", cities=cities)


#changed
@auth.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    session.pop('admin', None)
    session.clear()
    print('logged out')
    return redirect(url_for('auth.sign_up'))


