from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

googleLogin_URL = os.environ.get('googleLogin_URL') or "http://localhost:8080/authorize"
patient_URL = os.environ.get('patient_URL') or "http://localhost:5002/add-patient"

@app.route("/check_login/<string:userEmail>",methods=['POST'])
def check_login(userEmail):
    global doctor_URL
    doctor_URL = "http://doctor:5003/doctor/" + userEmail
    global pharmacy_URL
    # this pharmacy route is not implemented yet...
    pharmacy_URL = "http://pharmacy:5004/pharmacy/" + userEmail 
    global patient_URL
    patient_URL = "http://patient:5002/patient/" + userEmail 

    if request.is_json:
        try:
            profile = request.get_json()
            print(profile)
            
            profileType = profile["profileType"]
            if profileType == "doctor":
                doctor_result = invoke_http(doctor_URL, method='GET')
                return {
                        "code":201,
                        "data" : {
                            "doctor_result":doctor_result
                            }
                        }
                
            elif profileType == "patient":
                print(patient_URL)
                patient_result = invoke_http(patient_URL,method='GET' )
                return {
                        "code":201,
                        "data" : {
                            "patient_result":patient_result
                            }
                        }
            else:
                pharmacy_result = invoke_http(pharmacy_URL,method='GET')
                return {
                        "code":201,
                        "data" : {
                            "pharmacy_result":pharmacy_result
                            }
                        }

            return jsonify(result) , result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "manage_login.py internal error: " + ex_str
            }), 500
    



    


    

    
        
    
    





if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5110, debug=True)