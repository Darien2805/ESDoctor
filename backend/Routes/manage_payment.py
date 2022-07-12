from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
import requests
from invokes import invoke_http

import pika
import json
import amqp_email_setup

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
CORS(app)

update_order = os.environ.get('update_URL') or "http://order:5005/update-order"
order_URL = os.environ.get('order_URL') or "http://order:5005/order"

@app.route("/update_order/<string:orderId>", methods=['PUT'])
def update_orders(orderId):
    try:
        if orderId:
        
            print(orderId)
            print(update_order+orderId)
            order = invoke_http(update_order+'/'+orderId, method='PUT', json=request.get_json())
            print(order)
            print(order['code'])
            if order['code']==200:
                # send email to patient <-- for NX
                # info=request.get_json()
                #email=invoke_http(email_URL,method="POST",json=order['data'])
                # print(email)
                doc = invoke_http(order_URL+"/"+orderId)['data']
                print(str(doc))
                message = json.dumps(doc)
                amqp_email_setup.channel.basic_publish(exchange=amqp_email_setup.exchangename, routing_key="patient.payment.email", 
                body=message, properties=pika.BasicProperties(delivery_mode = 2))
                return jsonify(
                    {
                        "code": 200,
                        "message": "order status updated and email is sent to patient"
                    }
                )
                
            else:
                return jsonify(
                    {
                        "code": 401,
                        "message": "An Error Occurred."
                    }
                )
            
        return jsonify(
            {
                "code": 404,
                "message": "order not found."
            }
        ), 404
    except Exception as e:
        print(e)
        return jsonify(
            {
                "code": 503,
                "message": "Server error"
            }
        ), 503


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5102, debug=True)