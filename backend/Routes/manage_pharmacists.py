from flask import Flask, request, jsonify
from flask_cors import CORS

from email import message
import pika
import json
import amqp_email_setup

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

#appointment_URL = "http://localhost:5001/appointment"
patient_URL = os.environ.get('patient_URL') or "http://patient:5002/patient"
doctor_URL = os.environ.get('doctor_URL') or "http://doctor:5003/doctor"
order_URL = os.environ.get('order_URL') or "http://order:5005/order"
drug_URL = os.environ.get('drug_URL') or "http://drugs:5006/drugs"
update_order = os.environ.get('update_order') or "http://order:5005/update-order"


@app.route("/order_details/<string:orderId>")
def get_by_orderId(orderId):
    if orderId:
        #print(orderId)
        order_details={}

        print(patient_URL)
        print(doctor_URL)
        print(order_URL)
        print(drug_URL)
        print(update_order)

        #appointment = invoke_http(appointment_URL+"/"+orderId)
        #print(appointment)

        order = invoke_http(order_URL+"/"+orderId)
        print(order)

        #order comments
        order_details["comments"]=order['data']["otherComments"]
        print(order_details)
        #order status
        order_details["status"]=order['data']["status"]
        
        patientid = order['data']['customerID']
        print(patientid)
        
        patient = invoke_http(patient_URL+"/"+patientid)
        print(patient)
        #patient info
        order_details["patientName"]=patient['data']["patientName"]
        order_details["address"]=patient['data']["address"]
        order_details["drugAllergies"]=patient['data']["drugAllergies"]
        order_details["medicalHistory"]=patient['data']["medicalHistory"]
        order_details["contactNumber"]=patient['data']["contactNumber"]
        print(order_details)

        #order = invoke_http(order_URL+"/"+orderId)
        #print(order)

        #doctor info
        doctorid = order['data']['doctorID']
        print(doctorid)
        doctor = invoke_http(doctor_URL+"/"+doctorid)
        print(doctor)
        order_details["doctorName"] = doctor['data']["doctorName"]
        print(order_details)
        #drug info
        drugs = {}

        for i in range(len(order['data']["drugs"])//3):
            drugs[order['data']["drugs"][i*3]] = int(order['data']["drugs"][i*3+1])
        
        for key in drugs:
            print(key)
            drugData = invoke_http(drug_URL + "/" + key)
            print(drugData)
            price = drugData['drug']["Price"]
            quant = drugs[key]
            print("price: ",price)
            print("drugs[key]: ",drugs[key])
            drugs[key] = [quant * float(price),quant]
    

        return jsonify(
            {
                "code": 200,
                "data": [order_details, drugs]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "order not found."
        }
    ), 404
    pass

@app.route("/ship_order/<string:orderId>", methods=['PUT'])
def ship_order(orderId):
    try:
        if orderId:
        
            print(orderId)
            print(update_order+orderId)
            order = invoke_http(update_order+'/'+ orderId, method='PUT', json=request.get_json())
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
                amqp_email_setup.channel.basic_publish(exchange=amqp_email_setup.exchangename, routing_key="patient.order.email", 
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
    app.run(host="0.0.0.0", port=5103, debug=True)