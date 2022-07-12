import json
import os 
import amqp_email_setup
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
import datetime
monitorBindingKey="*.payment.email"

port = 465
#this email I create for our project 
email = "esdprojectT5@gmail.com"
password = "EsdProjectT5."


def send_payment_email(body):
    try:

        # edit according to sample data 
        data = dict(json.loads(body))
        patientID = data["customerID"]
        orderID = data["orderID"]
        total = data["total"]
        today = datetime.datetime.now()
        days = datetime.timedelta(days = 14)
        pay_day = (today + days).strftime('%d, %b %Y')
        context = ssl.create_default_context()
        message = MIMEMultipart("alternative")
        message["From"] = email
        message["To"] = f"{patientID}"
        message["From"] = email
        message["Subject"] = f"Payment Information"
        text = f"""
            Hi, <br />
            <br />
            Hope you're doing well. This is just to remind you that 
            <br />the invoice No: {orderID} with the total amount of {total} has been paid.
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
        return True 
    except Exception as e:
        print(str(e))
        traceback.print_exc()
        return False

def receivePaymentDetail():
    amqp_email_setup.check_setup()
    
    queue_name = "SendPaymentEmail"  

    # set up a consumer and start to wait for coming messages
    amqp_email_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_email_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived an error by " + __file__)
    send_payment_email(body)
    print() # print a new line feed


if __name__ == "__main__":
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_email_setup.exchangename))
    receivePaymentDetail()