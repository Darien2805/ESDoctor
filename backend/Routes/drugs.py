from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app
from invokes import invoke_http

from datetime import date

app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()
drugCollection = db.collection('drugs')

CORS(app)

class Appointment(object):

    def __init__(self, DrugName, Price):
        self.DrugName = DrugName
        self.price = Price

    def json(self):
        return {"DrugName": self.DrugName, "Price": self.Price}

#get all drugs
@app.route("/drugs")
def get_all_drugs():
    drugList = drugCollection.stream()
    allDrugs = [drug.to_dict() for drug in drugList]

    if len(allDrugs):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "drugs": allDrugs
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no drugs."
        }
    ), 404

#find by drugName
@app.route("/drugs/<string:drugName>")
def find_by_drugName(drugName):
    if drugName:
        try:
            query = drugCollection.where("DrugName", "==", drugName)
            docs = query.stream()
            for doc in docs:
                doc = doc.to_dict()
            return jsonify(
            {
                "code": 200,
                "drug": doc
            }
        )
        except:
            return jsonify(
                {
                    "code": 404,
                    "message": "drug not found."
                }
            ), 404
    else:
        return jsonify(
                {
                    "code": 404,
                    "message": "drug not found."
                }
            ), 404

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)