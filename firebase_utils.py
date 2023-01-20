import firebase_admin
from firebase_admin import db

cred_obj = firebase_admin.credentials.Certificate('./wine-b42b2-firebase-adminsdk-xaj0h-0558162e49.json')

default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://dbmanage-fbd05-default-rtdb.asia-southeast1.firebasedatabase.app/'
	})
ref = db.reference('/')

def initialize():
    return ref.get()

def insertPaymentData(data):
    addPayment = ref.child('WineDatabase/PaymentData')
    key = addPayment.push().key
    addPayment.child(key).set(data)
    return key

def updatePaymentData(data, key):
    addPayment = ref.child('WineDatabase/PaymentData')
    addPayment.child(key).set(data)

def listener(event):
    print('firebasedat',event.data)

def AccountListener():
    db.reference('WineDatabase/Category').listen(listener)