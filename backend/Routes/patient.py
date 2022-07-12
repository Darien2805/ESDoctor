from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# Initialize Firestore DB

cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()
patientCollection = db.collection('patients')



CORS(app)

class Patient(object):

    def __init__(self,patientID, patientName, drugAllergies, medicalHistory, address, emailAddress, contactNumber):
        self.patientName = patientName
        self.patientID = patientID
        #self.sex = sex
        self.drugAllergies = drugAllergies
        self.medicalHistory = medicalHistory
        #self.profileType = profileType
        self.address = address
        self.email = emailAddress
        self.contactNumber = contactNumber

    def json(self):
        return {"patientID": self.patientID, "patientName": self.patientName, "drugAllergies": self.drugAllergies, "medicalHistory": self.medicalHistory,"address": self.address, "email": self.emailAddress, "contactNumber" : self.contactNumber}


@app.route("/patient")
def get_all():
    patientList = patientCollection.stream() 
    allpatients = [patient.to_dict() for patient in patientList]

    if len(allpatients):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "patients": allpatients
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no patients."
        }
    ), 404


@app.route("/patient/<string:patientId>")
def find_by_isbn13(patientId):
    if patientId:
        patient = patientCollection.document(patientId).get()
        return jsonify(
            {
                "code": 200,
                "data": patient.to_dict()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "patient not found."
        }
    ), 404


@app.route("/add-patient", methods=['POST'])
def create_patient():
    patientID = request.json['patientID']
    print("SS"*50,patientID)
    print(patientID)
    data = request.get_json()
    try:
        patientCollection.document(patientID).set(data)
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the patient."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "message": "successfully created the patient!",
            "data": data
        }
    ), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
