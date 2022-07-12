from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app
#from sympy import Id
from invokes import invoke_http

from datetime import date

app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()
appointmentCollection = db.collection('Appointments')



CORS(app)

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
        return {"appointmentID": self.appointmentID, "patientID": self.patientID, "requestedTime": self.requestedTime, "chiefComplaint": self.chiefComplaint, "remarks": self.remarks, "status": self.status}


'''
@app.route("/appointment")
def get_all():
    appointmentList = appointmentCollection.stream()
    allAppointments = [appointment.to_dict() for appointment in appointmentList]


    if len(allAppointments):
        patientData=extractPatientsData()
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

def extractPatientsData():
    allPatients = invoke_http(patient_URL)['data']['patients']
    print(allPatients)
    data={}
    for patient in allPatients:
        data[patient["patientID"]]=patient
    return data

@app.route("/appointment/<string:appointmentId>")
def find_by_isbn13(appointmentId):
    if appointmentId:
        appointment = appointmentCollection.document(appointmentId).get().to_dict()
        isPatientValid = patientIsValid(appointment)

        patientData=extractPatientsData()
        appointment["patientName"]=patientData[appointment["patientID"]]["patientName"]
        appointment["drugAllergies"]=patientData[appointment["patientID"]]["drugAllergies"]
        appointment["medicalHistory"]=patientData[appointment["patientID"]]["medicalHistory"]

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



def patientIsValid(patientId):
    today = str(date.today())

    appointmentList = appointmentCollection.stream() 
    allAppointments = [appointment.to_dict() for appointment in appointmentList]
    
    if len(allAppointments):
        for i in range(len(allAppointments)):
            if allAppointments[i]["patientID"] == patientId and allAppointments[i]["requestedDate"] == today:
                return True
        else:
            return False
'''
#get all appointments
@app.route("/appointment")
def get_all_appointments():
    appointmentList = appointmentCollection.stream()
    allAppointments = [appointment.to_dict() for appointment in appointmentList]

    if len(allAppointments):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "appts": allAppointments
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no appointments."
        }
    ), 404

#find by appointmentID
@app.route("/appointment/<string:appointmentId>")
def find_by_patientID(appointmentId):
    if appointmentId:
        try:
            query = appointmentCollection.where("appointmentID", "==", appointmentId)
            docs = query.stream()
            for doc in docs:
                doc = doc.to_dict()
            return jsonify(
            {
                "code": 200,
                "data": doc
            }
        )
        except:
            return jsonify(
                {
                    "code": 404,
                    "message": "appointment not found."
                }
            ), 404
    else:
        return jsonify(
                {
                    "code": 404,
                    "message": "appointment not found."
                }
            ), 404

#find appointment by filtering patient
@app.route("/appointment_patientID/<string:patientId>")
def find_by_patientIDs(patientId):
    if patientId:
        try:
            data = []
            query = appointmentCollection.where("patientID", "==", patientId)
            docs = query.stream()
            for doc in docs:
                data.append(doc.to_dict())
            return jsonify(
            {
                "code": 200,
                "data": data
            }
        )
        except:
            return jsonify(
                {
                    "code": 400,
                    "message": "appointment not found."
                }
            ), 400
    else:
        return jsonify(
                {
                    "code": 400,
                    "message": "appointment not found."
                }
            ), 400

#add new appointment ** if patient has book an appointment on the day, throw an error
@app.route("/add-appointment", methods=['POST'])
def create_appointment():
    patientId = request.json['patientID']
    today = str(date.today())
    docs = appointmentCollection.where("patientID", "==", patientId).where("requestedDate", "==", today).stream()
    flag = False
    for doc in docs:
        flag = True
    print(flag)
    if (flag):
        return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred. Please try again."
                }
            ), 500
    else:
        data = request.get_json()
        print("here")
        doc = appointmentCollection.document().id
        data['appointmentID']= doc

        try:
            print("try")
            appointmentCollection.document(doc).set(data)

        except:
            print("except")
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

#update appointment status
@app.route('/update_appointment/<string:appointmentId>', methods=['PUT'])
def update(appointmentId):
    print("IM IN UPDATE APPT (PY)")
    try:
        print("can update")
        print(request.json)
        appointmentCollection.document(appointmentId).update(request.json)
        print("can update")
        return jsonify(
            {
                "code":200,
                "data": {"appointmentID": appointmentId,
                        "status": "accepted"},
                "message": "appointment Records Updated!"
            }    
        ), 200
    except Exception as e:
        print("CANNOT UPDATE")
        # print(e)
        return jsonify(
            {
                "code": 500,
                "message": "server error"
            }
        ), 500
        # return f"An Error Occurred: {e}"

if __name__ == '__main__':
    # find_by_isbn13("DPRs31ov7sftjAuNeM5U")
    app.run(host='0.0.0.0', port=5001, debug=True)
