from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# Initialize Firestore DB

cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()
pharCollection = db.collection('pharmacists')

CORS(app)
class Pharmacy(object):

    def __init__(self,pharID, pharName, emailAddress):
        self.pharName = pharName
        self.pharID = pharID
        self.email = emailAddress

    def json(self):
        return {"doctorID": self.doctorID, "patientName": self.doctorName, "email": self.emailAddress}


@app.route("/pharmacy")
def get_all():
    pharmacytList = pharCollection.stream() 
    allphar = [phar.to_dict() for phar in pharmacytList]

    if len(allphar):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "phar": allphar
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no pharmacists."
        }
    ), 404


@app.route("/pharmacy/<string:pharId>")
def find_by_isbn13(pharId):
    if pharId:
        phar = pharCollection.document(pharId).get()
        return jsonify(
            {
                "code": 200,
                "data": phar.to_dict()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "pharmacist not found."
        }
    ), 404


@app.route("/add-phar", methods=['POST'])
def create_phar():
    pharID = request.json['pharID']

    #print(doctorID)
    data = request.get_json()
    try:
        pharCollection.document(pharID).set(data)
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the pharmacist."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "message": "successfully created the pharmacist!",
            "data": data
        }
    ), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
