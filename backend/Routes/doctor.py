from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# Initialize Firestore DB

cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()
doctorCollection = db.collection('doctors')



CORS(app)

class Doctor(object):

    def __init__(self,doctorID, doctorName, email):
        self.doctorName = doctorName
        self.doctorID = doctorID
        self.email = email

    def json(self):
        return {
                "doctorID": self.doctorID, 
                "patientName": self.doctorName, 
                "email": self.email
                }


@app.route("/doctor/<string:doctorId>")
def find_by_isbn13(doctorId):
    if doctorId:
        doctor = doctorCollection.document(doctorId).get()
        return jsonify(
            {
                "code": 200,
                "data": doctor.to_dict()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "doctor not found."
        }
    ), 404


@app.route("/add-doctor", methods=['POST'])
def create_patient():
    doctorID = request.json['doctorID']

    data = request.get_json()
    try:
        doctorCollection.document(doctorID).set(data)
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the doctor."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "message": "successfully created the doctor!",
            "data": data
        }
    ), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
