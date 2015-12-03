import pika
from urllib import urlencode, urlopen


def sms(msg,phone):
    params = urlencode(
            {'api_key':'e282f7cbe915f6399e627a9469c08562131c82e7','message': 'Hi', 'phone':phone})
    response = urlopen("https://api.ringcaptcha.com/imu9yju8ozy4y5u4igob/code/sms", params)
    print response.read()
    return True






connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='probasemsg')

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    data=eval(body)
    for phone in data['subscribers']:
        print phone
        sms("hi",str(phone))
    print "sent sms to phone"
channel.basic_consume(callback,
                      queue='probasemsg',
                      no_ack=True)

try:
    print "start consuming"
    channel.start_consuming()
except Exception as e:
    print e
    pass

__author__ = 'gaurav'
