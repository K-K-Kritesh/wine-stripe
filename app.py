import json
from flask import Flask, jsonify, request as req, render_template
import stripe
import mysql.connector
import datetime
from mysql.connector import Error
import firebase_utils as firebase
import urllib.request
from createPdf import *
import os, time
import BusinessMailUtils as BMU
import ssl
from flask_cors import CORS, cross_origin



# stripe.api_key = "sk_test_51Lv3C7SITkrZ8wmukHf0ZndYK0tTa7Md5Q02LcV1knjMb8CT2sMuYdj659NFbpUUkzA94l2USbrDzBD3ajQLj59f00O4p5KEdT" # KKKGroup
stripe.api_key = "sk_test_51MIZxCSEFhL5FIrt8EzR369DGYdwLxsoeNv6fGvtWP76vvdSpKxcGH2iXi4t9MSiQcuYAZ798bF2RhPhNuCC6Qms00eKTTWreV"   # k-gmail
ssl._create_default_https_context = ssl._create_unverified_context 
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": '*'}})
# cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='wine')
    return conn

@app.route('/')
def home():
    # print(connection().is_connected())
    # firebase.initialize()
    # firebase.AccountListener()
    # createPDF();
    mail = BMU.BusinessMailUtils()
    dir = os.path.dirname(os.path.realpath('__file__'))
    path = os.path.join(dir, 'templates/receiptTemplet.html')
    html = ''
    with urllib.request.urlopen('file://'+path) as url:
        html = url.read()
    url = "http:google.com"
    status = mail.forgot_password_send_mail(html, 'kabariyakritesh65@gmail.com', "Forgot Password", "html", url)
    print(status)
    return str(connection())

@app.route('/Payment_method', methods=['POST'])
@cross_origin()
def paymentMethod():
    try:
        data = json.loads(req.data)
        customer_id = data['customer_id']
        product_id = data['product_id']
        quantity = data['quantity']
        currency = data['currency']
        product_data = data['product_data']
        checkout = stripe.checkout.Session.create(
            payment_method_types=['card'],
            success_url="http://localhost:3000/checkout?isPaid=success",
            cancel_url="http://localhost:3000/checkout?isPaid=failed",
            line_items=product_data,
            mode="payment",
        )
        print(checkout)
        data = insertPaymentInformation(customer_id, product_id, quantity, currency, checkout['id'], checkout['payment_status'], json.dumps(product_data).strip())
        key = firebase.insertPaymentData(data)
        
        return jsonify({
            'data': {'paymentUrl': checkout['url'], 'payment_detail': data, 'firebase_Key': key},
            'status':'failer' if data == "ALREADY" else 'success',
            'message':'Already' if data == "ALREADY" else 'Payment Status Pending'
        })
    except Exception as e:
        print(e)
        return {}
    
    

@app.route("/payment_status", methods=['POST'])
@cross_origin()
def paymentSuccess():
    p_id = req.form.get('p_id')
    id = req.form.get('id')
    key = req.form.get('f_key')
    status = stripe.checkout.Session.retrieve(p_id)
    print(status)
    data = updatePaymentInformation(id, status['payment_status'])
    firebase.updatePaymentData(data, key)
    return jsonify({
        'data': {'PaymentDetail': data, 'key': key},
        'status':'failer' if data == "ALREADY" else 'success',
        'message':'Already' if data == "ALREADY" else 'Payment Successfully'
    })


@app.route("/success")
def success():
    return render_template('success.html')

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

def insertPaymentInformation(*param):
    try:
        cn = connection()
        cur = cn.cursor()
        sql = f"INSERT INTO Purchase_Wine (customer_id, product_id, quantity, currency, p_stripe_id, payment_status, product_data) VALUES('{param[0]}','{param[1]}','{param[2]}','{param[3]}','{param[4]}','{param[5]}','{param[6]}')"
        cur.execute(sql)
        row_id = cur.lastrowid
        cn.commit()
        cur.execute(f"SELECT * from Purchase_Wine WHERE p_id = {row_id}")
        row_header = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data = dict(zip(row_header, result))
            json_data['created_date'] = f"{json_data['created_date']}"
        cur.close()
        return json_data
    except Exception as e:
        print(e)
        return "Failer"

def updatePaymentInformation(*param):
    try:
        cn = connection()
        cur = cn.cursor()
        cur.execute(f"SELECT * FROM Purchase_Wine WHERE p_id = {param[0]}")
        if len(cur.fetchall()) != 0:
            cur.execute(f"UPDATE Purchase_Wine set payment_status = '{param[1]}'  WHERE p_id = {param[0]}")
            cn.commit()
            cur.execute(f"SELECT * from Purchase_Wine WHERE p_id = {param[0]}")
            row_header = [x[0] for x in cur.description]
            rv = cur.fetchall()
            json_data = []
            for result in rv:
                json_data = dict(zip(row_header, result))
                json_data['created_date'] = f"{json_data['created_date']}"
            cur.close()
            return json_data
        else:
            return "NOT_FOUND"
    except Exception as e:
        return "failer"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug= True)