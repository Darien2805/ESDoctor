from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date
import os, sys

import requests
from invokes import invoke_http
import invokes


app = Flask(__name__)
CORS(app)

appointment_URL = os.environ.get('appointment_URL') or "http://appointment:5001/appointment"
patient_URL = os.environ.get('patient_URL') or "http://patient:5002/patient"
order_URL = os.environ.get('order_URL') or "http://order:5005/order"
drug_URL = os.environ.get('drug_URL') or "http://drugs:5006/drugs"

@app.route("/display_orders")
def get_all():
    
    allOrders = dict(invoke_http(order_URL))
    print("ALL ORDERS")
    print("ALL ORDERS")
    print(allOrders)
    print("ALL ORDERS")
    allOrders = allOrders['data']['orders']
    orders={}
    for order in allOrders:
        # print(order)
        orderID=order["orderID"]
        orders[orderID]=order
        # print(orders[orderID]["drugs"])
        drugList=orders[orderID]["drugs"]
        drugs=[]
        # print("hello",orders[orderID]["drugs"])
        for i in range(len(drugList)//3):
            drugs.append([drugList[i*3],drugList[i*3+1],drugList[i*3+2]])
        # print(drugs)
        orders[orderID]["drugs"]=drugs
        # print(orders)
        # patientData=dict(invoke_http(patient_URL + "/" + (order["customerID"])))["data"]
        # apptData=dict(invoke_http(appointment_URL + "/" + (order["orderID"])))["data"]
        patientData=dict(invoke_http(patient_URL + "/" + (order["customerID"])))
        apptData=dict(invoke_http(appointment_URL + "/" + (order["orderID"])))
        if('data' in patientData and 'data' in apptData):
            patientData = patientData['data']
            apptData = apptData['data']
            # print(apptData['drugAllergies'])
            orders[orderID]["drugAllergies"]=patientData['drugAllergies']
            orders[orderID]["patientName"]=patientData['patientName']
            orders[orderID]["requestedDate"]=apptData['requestedDate']
            orders[orderID]["requestedTime"]=apptData['requestedTime']
            # print("HEELOO")

    if len(allOrders):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": orders
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

@app.route("/display_order/<string:orderID>")
def get_order_by_orderID(orderID):
    if orderID:
        try:
            ordersInfo = dict(invoke_http(order_URL+"/"+orderID))
            if('data' in ordersInfo and 'orderID' in ordersInfo['data']):

                ordersInfo = ordersInfo['data']

                orderID=ordersInfo["orderID"]
                drugList=ordersInfo["drugs"]
                drugs=[]
                for i in range(len(drugList)//3):
                    drugs.append([drugList[i*3],drugList[i*3+1],drugList[i*3+2]])
                ordersInfo["drugs"]=drugs

                patientData=invoke_http(patient_URL + "/" + (ordersInfo["customerID"]))
                apptData=invoke_http(appointment_URL + "/" + (ordersInfo["orderID"]))
                if('data' in patientData and 'data' in apptData):
                    patientData = patientData['data']
                    ordersInfo["drugAllergies"]=patientData['drugAllergies']
                    ordersInfo["patientName"]=patientData['patientName']

                    apptData = apptData['data']
                    ordersInfo["requestedDate"]=apptData['requestedDate']
                    ordersInfo["requestedTime"]=apptData['requestedTime']
                    ordersInfo["chiefComplaint"]=apptData['chiefComplaint']
                
                    return jsonify(
                        {
                            "code": 200,
                            "data": ordersInfo
                        }
                    )
        except Exception as e:
            print(e)
            return jsonify(
                {
                    "code": 404,
                    "message": "Order not found."
                }
            ), 404

    return jsonify(
            {
                "code": 404,
                "message": "There are no orders."
            }
        ), 404

@app.route("/order_description/<string:patientID>")
def find_drug_by_orderID(patientID):
    
    allOrders = dict(invoke_http(order_URL))
    if('data' in allOrders):
        allOrders = allOrders['data']['orders']

    today = str(date.today())
    drugs={"consultation":1}

    for order in allOrders:
        orderID=order["orderID"]
        
        apptData=dict(invoke_http(appointment_URL + "/" + (order["orderID"])))
        if('data' in apptData):
            apptData = apptData['data']

            patient = apptData['patientID']
            apptdate = apptData['requestedDate']
            apptstatus = apptData['status']
            #if today == apptdate and patient == patientID and apptstatus == "accepted" and order["status"] == "Awaiting Payment":
            if patient == patientID and apptstatus == "accepted" and order["status"] == "Awaiting Payment":
                for i in range(len(order["drugs"])//3):
                    drugs[order["drugs"][i*3]] = int(order["drugs"][i*3+1])
                    orderID=order["orderID"]
                break
    
    print("drugs: ",drugs)

    for key in drugs:
        print(key)
        drugData = invoke_http(drug_URL + "/" + key)
        print(drugData)
        price = drugData['drug']["Price"]
        quant = drugs[key]
        print("price: ",price)
        print("drugs[key]: ",drugs[key])
        drugs[key] = [quant * float(price),quant]
    
    if (len(drugs)>1):
        print(len(drugs)>1)
        print(drugs)
        return jsonify({
            "code": 200,
            "data": [drugs, orderID]
        })
    return jsonify({
            "code": 404,
            "message": "There are currently no outstanding orders."
        }), 404

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=True)