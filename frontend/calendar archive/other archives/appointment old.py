from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app
#from sympy import Id

app = Flask(__name__)

#Notes for team: IDK how to put appointment status...Maybe another microservice?

# Initialize Firestore DB

cred = credentials.Certificate('../key.json')
default_app = initialize_app(cred)
db = firestore.client()
appointmentCollection = db.collection('Appointments')



CORS(app)
# need to import models probably need to work on this some other drugAllergies, lemme just set up the routes first

#here we can change the models appropriately according to the dataset you need, imma google and OT OT edit
class Appointment(object):

    def __init__(self, appointmentID, patientID, requestedDate, requestedTime, chiefComplaint, remarks, status):
        self.appointmentID = appointmentID
        self.patientID = patientID
        self.requestedDate = requestedDate
        self.requestedTime = requestedTime
        self.chiefComplaint = chiefComplaint
        self.remarks = remarks
        self.status = status
    def json(self):
        return {"patientID": self.patientID, "requestedTime": self.requestedTime, "chiefComplaint": self.chiefComplaint, "remarks": self.remarks, "status": self.status}



@app.route("/appointment")
def get_all():
    appointmentList = appointmentCollection.stream() 
    allAppointments = [appointment.to_dict() for appointment in appointmentList]

    if len(allAppointments):
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


@app.route("/appointment/<string:appointmentId>")
def find_by_isbn13(appointmentId):
    if appointmentId:
        appointment = appointmentCollection.document(appointmentId).get()
        return jsonify(
            {
                "code": 200,
                "data": appointment.to_dict()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "appointment not found."
        }
    ), 404


@app.route("/add-appointment", methods=['POST'])
def create_appointment():
    #appointmentID = request.json['appointmentID']
    appointmentDate = request.json['requestedDate']
    #request.json['appointmentID'] = appointmentCollection.document()
    #print(appointmentID)
    data = request.get_json()
    
    print(data)
    doc = appointmentCollection.document().id
    #docid = doc.id()
    #print(docid)
    data['appointmentID']= doc
    print(doc)
    try:
        appointmentCollection.document(doc).set(data)
        #date = appointmentCollection.document(appointmentDate)
        #date.document(appointmentID).set(data)
        #appointmentCollection.document(appointmentDate).collection(appointmentID).document().set(data)
        #appointmentCollection.document(appointmentDate).set(data)
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred. Please try again."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "message": "successfully created the appointment!",
            "data": data
        }
    ), 201

@app.route('/update-appointment/<string:appointmentId>', methods=['PUT'])
def update(appointmentId):
    try:
        
        appointmentCollection.document(appointmentId).update(request.json)
        return jsonify(
            {
                "message": "appointment Records Updated!",
                "success": True
            }    
        ), 200
    except Exception as e:
        return f"An Error Occurred: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
