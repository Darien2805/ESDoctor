from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
from firebase_admin import credentials, firestore, initialize_app
from invokes import invoke_http
app = Flask(__name__)
from datetime import date
import datetime
# Initialize Firestore DB

cred = credentials.Certificate('./key.json')
default_app = initialize_app(cred)
db = firestore.client()
orderCollection = db.collection('orders')


CORS(app)
# need to import models probably need to work on this some other time, lemme just set up the routes first

#here we can change the models appropriately according to the dataset you need, imma google and OT OT edit
class Order(object):

    def __init__(self, orderID, customerID, doctorID, time, drugs, otherComments, status):
        self.orderID = orderID
        self.customerID = customerID
        self.doctorID = doctorID
        self.time = time
        self.drugs = drugs
        self.otherComments=otherComments
        self.status=status

    def json(self):
        return {"orderID": self.orderID, "customerID": self.customerID, "doctorID": self.doctorID, "time": self.time, "drugs": self.drugs,"otherComments":self.otherComments, "status": self.status}

'''
@app.route("/order")
def get_all():
    orderList = orderCollection.stream() 
    allOrders = [order.to_dict() for order in orderList]
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
        apptData=extractApptData(order["orderID"])["data"]
        # print(apptData['drugAllergies'])
        orders[orderID]["drugAllergies"]=apptData['drugAllergies']
        orders[orderID]["patientName"]=apptData['patientName']
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
def extractApptData(apptID):
    appt_URL = "http://localhost:5001/appointment"+"/"+apptID
    # print(appt_URL+"BOO")
    apptInfo = invoke_http(appt_URL)
    # print("hereXD")
    # print(apptInfo)
    return apptInfo


@app.route("/order/<string:orderID>")
def find_by_orderID(orderID):
    print("orderID: ",orderID)
    if orderID:
        order = orderCollection.document(orderID).get().to_dict()
        # print(order)
        apptData=extractApptData(orderID)['data']
        print(apptData)
        order["drugAllergies"]=apptData['drugAllergies']
        order["patientName"]=apptData['patientName']
        order["requestedDate"]=apptData['requestedDate']
        order["requestedTime"]=apptData['requestedTime']
        order["chiefComplaint"]=apptData['chiefComplaint']

        # making drugs into nested list
        drugs=[]
        # print("hello",orders[orderID]["drugs"])
        for i in range(len(order["drugs"])//3):
            drugs.append([order["drugs"][i*3],order["drugs"][i*3+1],order["drugs"][i*3+2]])
        # print(drugs)
        order["drugs"]=drugs
        # print("HI")

        return jsonify(
            {
                "code": 200,
                "data": order
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "order not found."
        }
    ), 404

@app.route("/order_drug/<string:patientID>")
def find_drugby_orderID(patientID):
    orderList = orderCollection.stream() 
    allOrders = [order.to_dict() for order in orderList]

    today = str(date.today())
    drugs={"consultation":1}

    for order in allOrders:
        orderID=order["orderID"]
        
        apptData=extractApptData(order["orderID"])["data"]
        patient = apptData['patientID']
        apptdate = apptData['requestedDate']
        apptstatus = apptData['status']
        if today == apptdate and patient == patientID and apptstatus == "accepted" and order["status"] == "Awaiting Payment":
            for i in range(len(order["drugs"])//3):
                drugs[order["drugs"][i*3]] = int(order["drugs"][i*3+1])
                orderID=order["orderID"]
            break
    print("drugs: ",drugs)
    for key in drugs:
        fields = drugCollection.document(key).get().to_dict()

        price = fields["Price"]
        quant = drugs[key]
        print("price: ",price)
        print("drugs[key]: ",drugs[key])
        drugs[key] = [quant * float(price),quant]
    if (len(drugs)>1):
        print(len(drugs)>1)
        print(drugs)
        return jsonify(
        {
            "code": 200,
            "data": [drugs, orderID]
        }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are currently no outstanding orders."
        }
    ), 404
    '''
#get all orders
@app.route("/order")
def get_all():
    orderList = orderCollection.stream() 
    allOrders = [order.to_dict() for order in orderList]
    if len(allOrders):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": allOrders
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

#find order by orderID
@app.route('/order/<string:orderId>')
def find_by_orderId(orderId):
    if orderId:
        order = orderCollection.document(orderId).get()
        return jsonify(
            {
                "code": 200,
                "data": order.to_dict()
            }
        )
        
    else:
        return jsonify(
            {
                "code": 404,
                "message": "order not found."
            }
        ), 404

#update order
@app.route('/update-order/<string:orderId>', methods=['PUT'])
def update(orderId):
    try:
        print(orderId) 

        orderCollection.document(orderId).update(request.json)
        return jsonify(
            {
                "code": 200,
                "message": "Order Records Updated!",
                "success": True
            }    
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 503,
                "message": "error"
            }
        ), 503

#adds order
@app.route("/add-order", methods=['POST'])
def create_Order():
    # print("IM HERE")
    data = request.get_json()
    orderId = data['orderID']

    try:
        orderCollection.document(orderId).set(data)
        
    except:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the Order."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "message": "successfully created the Order!",
            "data": data
        }
    ), 201
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
