import ast
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


cred = credentials.Certificate('./key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/test", methods=["POST"])
def test():
    data = str(request.data)

    ast.literal_eval(data)
    response = {
                "code": 200,
                "msg": "user doesn't exist, please register",
                "profileType": "",
                "data": data
            }
    print(data)
    return jsonify(
            response
        ), 200
@app.route("/googleLogin", methods=["POST"])
def google_login():
    data = dict(request.form)
    print(data)
    acc = data["tv"]

    #check if acc exist, if not ==> 302
    user_exist = user_existed(acc)
    print(user_exist)

    #if user exist, return data
    if user_exist:
        usr_info  = get_usr_data(acc)
        print(usr_info["tv"])
        print("DICT",dict(usr_info))
        return jsonify(
            {
                "code": 200,
                "msg": "google log in successfully",
                "profileType": usr_info["profileType"],
                "id":usr_info["tv"]
            }
        ), 200
    return jsonify(
            {
                "code": 301,
                "msg": "user doesn't exist, please register",
                "profileType": ""
            }
        ), 301


@app.route("/register", methods=["POST"])
def register():
    data = dict(request.form)
    acc = data["tv"]
    try:
        doc_ref = db.collection(u'google_login').document(acc)
        print(data["profileType"])
        doc_ref.set(data)
        return jsonify(
            {
                "code": 200,
                "msg": "google log in successfully",
                "profileType": data["profileType"],
                "id": acc
            }
        ), 200
    except:
        return jsonify(
            {
                "code": 500,
                "msg": "server error"
            }
        ),500
def get_usr_data(user_acc):
    account_ref = db.collection(u'google_login').stream()

    docs = account_ref
    print(docs)
    for doc in docs:
        if doc.id == user_acc:
            return doc.to_dict()
    return None

def user_existed(user_acc):
    acc_info_list = db.collection(u'google_login').stream()
    print("LIST",acc_info_list)
    print("us",user_acc)
    for info in acc_info_list:
        print("&&"*30,info.id, user_acc, info.id == user_acc)
        if info.id == user_acc:
            return True 
    return False

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7000, debug=True)