# use flask framework for classification model
import imghdr

from flask import *
from flask_mail import Mail, Message
import tensorflow as tf
import os
from werkzeug.utils import secure_filename
import keras
from keras.models import load_model
import numpy as np
import pandas as pd
import sqlite3
import qrcode
from PIL import Image
import base64
import io
import imghdr


# ---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tsfyguaistyatuis589566875623568956'
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'thembankumane590@gmail.com'
app.config['MAIL_PASSWORD'] = 'ehchhgorqnwgfxtj'
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)

# --------------Database code-----------------------------
# --------------Register user to database-----------------
def register_to_db(title, fName, lName, status):
    #     establish connection with database
    conn = sqlite3.connect('database/database.db')
    cur = conn.cursor()
    # insert into database query
    cur.execute('INSERT INTO rsvp (title, first_name, last_name, attend) VALUES (?, ?, ?, ?)', (title, fName, lName, status))
    conn.commit()
    conn.close()

# ---------------check if user is registered in the database
def check_user(title, fName, lName, status):
    #     establish connection with database
    conn = sqlite3.connect('database/database.db')
    cur = conn.cursor()
    # cur.execute('SELECT * FROM rsvp',
    #             (title, fName, lName, status))
    table = pd.read_sql_query("SELECT * FROM rsvp", conn)
    print(table)

    if table.empty:
        return False;
    else:
        return True

# ------------------End of database-----------------------
# ------------------Generate QR Code----------------------
def generate_qr_code(fName, lName):
    features = qrcode.QRCode(version=1, box_size=40, border=3)
    features.add_data(fName + " " + lName)
    features.make(fit=True)
    generate_code = features.make_image(fill_color='black', back_color='white')
    path = 'static/' + 'qr_codes/' + fName + "_" + lName + ".png"
    fileName = fName + "_" + lName + ".png"
    generate_code.save(path)
    return fileName

# --------------------------------------------------------
#-------------------Display image in html----------------
@app.route('/<filepath>')
def display_image(filename):

    return redirect(url_for('static', filename = '/qr_codes/' + filename, code = 301))

# ------------------Download option for user--------------
@app.route('/download_qr_code')
def download_qr_code(file):
    file_path = 'static/qr_codes/' + file
    return send_file(file_path)
# ------------------Go to main file-----------------------
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/', methods=['GET', 'POST'])
def fetch_data():
    # fetch data from html form
    if request.method == 'POST':
        # fetch data from html file
        title = request.form['title']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        availability = request.form.get('checkbox')
        print(availability)

        # call function
        # pass data to database
        register_to_db(title, first_name, last_name, availability)
        check_user(title, first_name, last_name, availability)
        # -----Generate QR Code with first and last name
        filename = generate_qr_code(first_name, last_name)
        # display image in html page
        display_image(filename)
        # -----Download QR Code------------------------
        download_qr_code(filename)
        #  send email
        send_mail(email, filename)

        flash('Thank you for your time, we look forward to see you in the launch.')
        flash('We have emailed your unique QR Code.')

        return render_template('main.html', filename = filename)
    return None
# ----------------------------------------------------------------------------------------
@app.route('/send_mail/<email>', methods=['GET'])
def send_mail(email, filename):
    msg_title = 'AI HUB LAUNCH, 24 March 2023'
    sender = 'thembankumane590@gmail.com'
    msg_body = 'Please join us for the launch of AI HUB at TUT Pretoria main campus on the 24th of March 2020.' \
          'Attached is your QR Code for entry.' \

    msg = Message(msg_title, sender=sender, recipients=[email])

    data = {
        'app_name': 'AI HUB TUT',
        'title': msg_title,
        'body': msg_body,
    }

    msg.html = render_template('email.html', data=data)
    # Add attachment
    with app.open_resource('static/qr_codes/'+filename) as fp:
        msg.attach('static/qr_codes/'+filename, 'image/png', fp.read())

    with app.open_resource('static/attachments/Invite_AI_Hub_Launch.pdf') as fp:
        msg.attach('static/attachments/Invite_AI_Hub_Launch.pdf', 'application/pdf', fp.read())

    # send email
    try:
        mail.send(msg)
        return 'Email Sent'
    except Exception as e:
        return '{e}'

# -----------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)