from flask import Flask, render_template, request, url_for, flash, redirect
import mysql.connector
from datetime import datetime
from input_handler import handle_null_int, handle_null_str
import dotenv
import os


def execute_insert_query(query, data):
    try:
        cursor.execute(query, data)
        cnx.commit()
        return 'Done'
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        if 'Duplicate entry' in str(err):
            print(str(err))
            return 'Duplicate'


def execute_read_query(query):
    out = None
    try:
        cursor.execute(query)
        out = cursor.fetchall()
        return out
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))


dotenv.load_dotenv(override=True)
cnx = mysql.connector.connect(user='root', password=os.getenv('SQL_PASS'),
                              host='127.0.0.1',
                              database='Divar')
cursor = cnx.cursor()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    ads = execute_read_query("SELECT * FROM Advertise")
    return render_template('index.html', items=ads[-10:])


@app.route("/signup/", methods=['GET', 'POST'])
def sign_up():
    cities = execute_read_query("SELECT City FROM Region")
    add_user = ("INSERT INTO NormalUser "
                "(IsActive, FirstName, LastName, RegisteredAt, Email, Phone, City, Street, House_num) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

    if request.method == 'POST':
        in_f_name = handle_null_str(request.form['inFName'])
        in_l_name = handle_null_str(request.form['inLName'])
        in_phone = handle_null_str(request.form['inPhone'])
        in_email = handle_null_str(request.form['inEmail'])
        in_city = handle_null_str(request.form['uCity'])
        in_street = handle_null_str(request.form['inStreet'])
        in_house_num = handle_null_int(request.form['inHouseNum'])

        data_n_user = (1, in_f_name, in_l_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), in_email,
                       in_phone, in_city, in_street, in_house_num)

        if not in_email and not in_phone:
            flash('One of Email or Phone is required!')
            return redirect(url_for('sign_up'))
        if in_street is None and in_house_num is not None:
            flash('Please enter street name!')
            return redirect(url_for('sign_up'))
        else:
            user_insertion = execute_insert_query(add_user, data_n_user)
            if user_insertion == 'Done':
                return redirect(url_for('index'))
            else:
                flash('email or phone is duplicate.Try another')
                return redirect(url_for('sign_up'))
    else:   # GET
        return render_template("signup.html", cities=cities)


if __name__ == '__main__':
    app.debug = True
    app.run()
    cursor.close()
    cnx.close()
