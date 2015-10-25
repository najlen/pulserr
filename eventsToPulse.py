#!/usr/bin/env python3

"""
Consume events from rabbit queue and identify pulses. 
Push pulses back to rabbit, in new queue.
"""

__author__ = 'Daniel Nihlen'
__version__ = '0.1'
__date__ = '2015-09-12'

import pika, json
from pprint import pprint as pp
from datetime import datetime
import dateutil.parser


global last_value
global rising 
rising = True
last_value = 0

global channel

def init_rabbit():
    global channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='pulse', type='fanout')
    channel.queue_declare(queue='pulserr_raw')


def pulse(data):
    '''Pulse detected'''
    body = {'time': data['time'], 'sensor': data['sensor']}
    print("\nPulse published {}".format(json.dumps(body)))
    channel.basic_publish(exchange='pulse', routing_key='', body=json.dumps(body))

def identify_pulse(json_data):
    '''Consume events and identify pulses. Rise and fall in event value is a pulse'''
    global last_value
    global rising
    data = json.loads(json_data.decode("utf-8"))
    if last_value < data['value']:
        print("| Rising {} -> {} ".format(last_value, data['value']), end="")
        rising = True
    else:
        print("| Falling {} -> {}".format(last_value, data['value']), end="")
        if rising:
            pulse(data)
        rising = False    
    last_value = data['value']

def event_callback(ch, method, properties, body):
    #print("eventsToPulse received {}".format(body))
    identify_pulse(body)

def main():
    init_rabbit()
    channel.basic_consume(event_callback, queue='pulserr_raw', no_ack=True)
    channel.start_consuming()
        
main()
