import pika
from os import environ

hostname = "esd-rabbit" #environ.get('rabbit_host') or 'localhost' ###
port = environ.get('rabbit_port') or 5672 ###
connectionPara =  pika.ConnectionParameters(
        host=hostname, port=port,
        heartbeat=3600, blocked_connection_timeout=3600, )
connection = pika.BlockingConnection(connectionPara)

channel = connection.channel()
# Set up the exchange if the exchange doesn't exist
# - use a 'topic' exchange to enable interaction
exchangename="order_topic"
exchangetype="topic"
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)

queue_name = 'Error'
channel.queue_declare(queue=queue_name, durable=True) 

channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.error') 

queue_name = 'SendPaymentEmail'
channel.queue_declare(queue=queue_name, durable=True)

channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.payment.email') 

queue_name = 'SendTimeslotEmail'
channel.queue_declare(queue=queue_name, durable=True)

channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.timeslot.email') 

queue_name = 'SendOrderEmail'
channel.queue_declare(queue=queue_name, durable=True)

channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='*.order.email') 





def check_setup():

    global connection, channel, hostname, port, exchangename, exchangetype

    if not is_connection_open(connection):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port, heartbeat=3600, blocked_connection_timeout=3600))
    if channel.is_closed:
        channel = connection.channel()
        channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True)


def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        print("...creating a new connection.")
        return False
