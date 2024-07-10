from flask import request, session, Blueprint, render_template, url_for, flash, redirect
import datetime
from app.input_handler import *
from app.mysql_db import *
from app.utils import redis_cache
import random
import json

auth = Blueprint('auth', __name__)
# This file is completely checked by M


def generate_otp(length=6):
    return ''.join(random.choices('0123456789', k=length))


@auth.route('/user_request_otp/', methods=['POST', 'GET'])
def user_request_otp():
    if request.method == 'POST':
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])

        user_id = execute_read_query("SELECT UserID FROM NormalUser WHERE Email= '{}'".format(in_email), False)
        if user_id is None:
            user_id = execute_read_query("SELECT UserID FROM NormalUser WHERE Phone ='{}'".format(in_phone), False)

        if user_id is None:
            flash('user did not found')
            return redirect(url_for('auth.user_request_otp'))

        otp = generate_otp()
        if redis_cache.exists('N'+str(user_id['UserID'])):
            redis_cache.delete('N'+str(user_id['UserID']))

        redis_cache.setex('N'+str(user_id['UserID']), 60000, otp)
        print('in 1 in post', otp)
        return redirect(url_for('auth.user_validate_otp', messages=json.dumps({'otp': otp,
                                                                               'user_id': user_id['UserID'],
                                                                               'email': request.form['inEmail'],
                                                                               'phone': request.form['inPhone']})))

    elif request.method == 'GET':
        return render_template("./auth/user_login.html")


@auth.route('/user_validate_otp/', methods=['POST', 'GET'])
def user_validate_otp():
    if request.method == 'GET':
        data = json.loads(request.args.get('messages'))
        print(data)
        user_id = handle_null_str(data['user_id'])
        email = data['email']
        phone = data['phone']
        stored_otp = redis_cache.get('N' + str(user_id))
        print('in 2 in get', stored_otp)
        flash('OTP is: ' + stored_otp)
        return render_template("./auth/user_login_val.html", user={'email': email, 'phone': phone,
                                                                   'user_id': user_id})

    elif request.method == 'POST':
        user_id = handle_null_str(request.form['user_id'])
        input_otp = request.form['inOTP']
        email = request.form['inEmail']
        phone = request.form['inPhone']
        stored_otp = redis_cache.get('N' + str(user_id))
        print('in 2 in post - stored , in', stored_otp, input_otp)

        if stored_otp is None:
            flash('OTP expired or not set')
            return redirect(url_for('auth.user_request_otp'))

        if input_otp != stored_otp:
            flash('Invalid OTP. OTP is: ' + stored_otp)
            return render_template("./auth/user_login_val.html", user={'email': email, 'phone': phone,
                                                                       'userId': user_id})
        elif input_otp == stored_otp:
            print('in N delete')
            redis_cache.delete('N'+str(user_id))
            session['logged_in'] = True
            session['user'] = user_id
            session['admin'] = False
            return redirect(url_for('market.home'))


@auth.route('/admin_request_otp/', methods=['POST', 'GET'])
def admin_request_otp():
    if request.method == 'POST':
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])

        user_id = execute_read_query("SELECT AUserID FROM AdminUser WHERE Email= '{}'".format(in_email), False)
        if user_id is None:
            user_id = execute_read_query("SELECT AUserID FROM AdminUser WHERE Phone ='{}'".format(in_phone), False)

        if user_id is None:
            flash('user did not found')
            return redirect(url_for('auth.admin_request_otp'))

        otp = generate_otp()
        if redis_cache.exists('A' + str(user_id['AUserID'])):
            redis_cache.delete('A' + str(user_id['AUserID']))

        redis_cache.setex('A' + str(user_id['AUserID']), 60000, otp)
        print('in 1 in post', otp)
        return redirect(url_for('auth.admin_validate_otp', messages=json.dumps({'otp': otp,
                                                                                'user_id': user_id['AUserID'],
                                                                                'email': request.form['inEmail'],
                                                                                'phone': request.form['inPhone']})))
    elif request.method == 'GET':
        return render_template("./auth/user_login.html")


@auth.route('/admin_validate_otp/', methods=['POST', 'GET'])
def admin_validate_otp():
    if request.method == 'GET':
        data = json.loads(request.args.get('messages'))
        print(data)
        user_id = handle_null_str(data['user_id'])
        email = data['email']
        phone = data['phone']
        stored_otp = redis_cache.get('A' + str(user_id))
        print('in 2 in get', stored_otp)
        flash('OTP is: ' + stored_otp)
        return render_template("./auth/user_login_val.html", user={'email': email, 'phone': phone,
                                                                   'user_id': user_id})

    elif request.method == 'POST':
        user_id = handle_null_str(request.form['user_id'])
        print(user_id)
        input_otp = request.form['inOTP']
        email = request.form['inEmail']
        phone = request.form['inPhone']
        stored_otp = redis_cache.get('A' + str(user_id))
        print('in 2 in post - stored , in', stored_otp, input_otp)

        if stored_otp is None:
            flash('OTP expired or not set')
            return redirect(url_for('auth.user_request_otp'))

        if input_otp != stored_otp:
            print('here')
            flash('wrong OTP. OTP is: ' + stored_otp)
            return render_template("./auth/user_login_val.html", user={'email': email, 'phone': phone,
                                                                       'userId': user_id})
        elif input_otp == stored_otp:
            print('in A delete')
            redis_cache.delete('A'+str(user_id))
            session['logged_in'] = True
            session['user'] = user_id
            session['admin'] = True
            return redirect(url_for('admin.admin_home'))


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
        if 'logged_in' in session:
            if session['admin']:
                return redirect(url_for('admin.home'))
            else:
                return redirect(url_for('market.home'))
        else:
            cities = execute_read_query("SELECT City FROM Region", True)
            print(cities)
            return render_template("auth/signup.html", cities=cities)


@auth.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('logged_in', None)
    session.pop('admin', None)
    session.clear()
    print('logged out')
    return redirect(url_for('market.index'))
