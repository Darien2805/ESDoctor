from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
#from isort import code

import requests
from invokes import invoke_http

from email import message
import pika
import json
import amqp_email_setup
from flask import Flask, request, jsonify
from flask_cors import CORS
import os 

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# import json

app = Flask(__name__)
CORS(app)

patient_URL = os.environ.get('patient_URL') or "http://patient:5002/patient"
appointment_URL = os.environ.get('appointment_URL')  or "http://appointment:5001/appointment"
updateAppt_URL = os.environ.get('updateAppt_URL')  or "http://appointment:5001/update_appointment"


@app.route("/display_appointment")
def get_all():

    
    allAppointments = dict(invoke_http(appointment_URL))
    if('data' in allAppointments):
        allAppointments = allAppointments['data']['appts']

    
    # print(patient_URL)
    # print(appointment_URL)
    # print(email_URL)

    allPatients = dict(invoke_http(patient_URL))
    if('data' in allPatients):
        allPatients = allPatients['data']['patients']
    
    
    
    patientData={}
    for patient in allPatients:
        patientData[patient["patientID"]]=patient
    # print(patientData)


    if len(allAppointments):
        for i in range(len(allAppointments)):
            
            allAppointments[i]["patientName"]=patientData[allAppointments[i]["patientID"]]["patientName"]
            allAppointments[i]["drugAllergies"]=patientData[allAppointments[i]["patientID"]]["drugAllergies"]
            allAppointments[i]["medicalHistory"]=patientData[allAppointments[i]["patientID"]]["medicalHistory"]

        return jsonify(
            {
                "code": 200,
                "data": {
                    "appointments": allAppointments
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no appointments."
        }
    ), 404

@app.route("/manage_appointment/<string:appointmentId>")
def find_by_appointmentId(appointmentId):
    if appointmentId:
        appointment = invoke_http(appointment_URL+"/"+appointmentId)
        print(appointment)
        patientid = appointment['data']['patientID']
        patient = invoke_http(patient_URL+"/"+patientid)

        appointment["patientName"]=patient['data']["patientName"]
        appointment["drugAllergies"]=patient['data']["drugAllergies"]
        appointment["medicalHistory"]=patient['data']["medicalHistory"]

        return jsonify(
            {
                "code": 200,
                "data": appointment
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "appointment not found."
        }
    ), 404

# to update the status of the appt
@app.route("/update-appointment/<string:appointmentId>", methods=['PUT'])
def update_appointment(appointmentId):
    
    
    try:
        if appointmentId:
            # update the appointment 
            print(appointmentId)
            # inp={"status":"accepted"}json.dumps(inp)
            print(updateAppt_URL+"/"+appointmentId)
            appointment = invoke_http(updateAppt_URL+"/"+appointmentId, method='PUT', json=request.get_json())
            
            # {'code': 200, 'data': {'appointmentID': 'apptID', 'status': 'accepted'}, 'message': 'appointment Records Updated!'}
            print(appointment)
            

            if appointment['code']==200:
                print("="*20)
                # send email to patient <-- for NX
                # info=request.get_json()
                # email=invoke_http(email_URL,method="POST",json=appointment['data'])
                # print(email)
                #doc = db.collection(u'Appointments').document(appointmentId).get()
                doc = invoke_http(appointment_URL+"/"+appointmentId)["data"]
                #info = doc.to_dict()
                message = json.dumps(doc)
                amqp_email_setup.channel.basic_publish(exchange=amqp_email_setup.exchangename, routing_key="patient.timeslot.email", 
                    body=message, properties=pika.BasicProperties(delivery_mode = 2))
                return jsonify(
                    {
                        "code": 200,
                        "message": "appointment status updated and email is sent to patient"
                    }
                )
                
            else:
                return jsonify(
                    {
                        "code": 401,
                        "message": "An Error Occurred."
                    }
                )
        
    except Exception as e:
        return jsonify(
            {
                "code": 404,
                "message": "Appointment not found or an error occurred."
            }
    ), 404

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)