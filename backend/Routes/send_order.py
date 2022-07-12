import json
import os 
import amqp_email_setup
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

monitorBindingKey="*.order.email"

port = 465
#this email I create for our project 
email = "esdprojectT5@gmail.com"
password = "EsdProjectT5."


def send_order_email(body):
    try:
        # edit according to sample data 
        data = dict(json.loads(body))
        patientID = data["customerID"]
        context = ssl.create_default_context()
        message = MIMEMultipart("alternative")
        message["From"] = email
        message["To"] = f"{patientID}"
        message["From"] = email
        message["Subject"] = f"Order Confirmation"
        text = f"""
            Hi, <br />
            <br />
            Thank you for your order!
            <br />
            <br />
            You will receive your order by today. <br />
            If you have any enquries, please contact us by replying this email.
            <br />
            <br />
            If you have any question, please contact us.
            <br />
            <br />
            Sincerely, <br /> 
            ESDTelemedicine Team
            """
        html = MIMEText(text,"html")
        message.attach(html)
        with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
            server.login(email,password)
            server.sendmail(email,patientID,message.as_string())
        print("email sent")
        print("email sent to:", patientID)
        return True 
        
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        print("email not sent to", patientID)
        return False
        
def receiveOrderDetail():
    amqp_email_setup.check_setup()
    
    queue_name = "SendOrderEmail"  

    # set up a consumer and start to wait for coming messages
    amqp_email_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_email_setup.channel.start_consuming()
    print(queue_name)

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an error by " + __file__)
    # processPayment(body)
    send_order_email(body)
    print() # print a new line feed

if __name__ == "__main__":
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_email_setup.exchangename))
    receiveOrderDetail()