import json
import os 
import amqp_email_setup
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback

monitorBindingKey="*.timeslot.email"

port = 465
#this email I create for our project 
email = "esdprojectT5@gmail.com"
password = "EsdProjectT5."


def send_timeslot_email(body):
    try:

        # edit according to sample data 
        data = dict(json.loads(body))
        patientID = data["patientID"]
        requestedDate = data["requestedDate"]
        requestedTime = data["requestedTime"]

        context = ssl.create_default_context()
        message = MIMEMultipart("alternative")
        message["From"] = email
        message["To"] = f"{patientID}"
        message["From"] = email
        message["Subject"] = f"Timeslot Information"
        text = f"""\
            Hi, <br />
            <br />
            Your upcoming appointment with us is on <b>{requestedDate}</b> at <b>{requestedTime}</b>. <br />
            If you need to reschedule, please reply to this email:<b> {email}</b>.
            <br />
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

def receiveTimeSlotDetail():
    amqp_email_setup.check_setup()
    
    queue_name = "SendTimeslotEmail"  

    # set up a consumer and start to wait for coming messages
    amqp_email_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_email_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived by " + __file__)
    send_timeslot_email(body)
    print() # print a new line feed


if __name__ == "__main__":
    print("\nThis is " + os.path.basename(__file__), end='')
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_email_setup.exchangename))
    receiveTimeSlotDetail()