#!/usr/bin/env python3

"""
Consume events from rabbit queue and identify pulses. 
Push pulses back to rabbit, in new queue.
"""

__author__ = 'Daniel Nihlen'
__version__ = '0.1'
__date__ = '2015-09-12'

import pika
import json
from pprint import pprint as pp
import datetime

global last_value
global rising 
rising = True
last_value = 0


def init_rabbit():
    global event_channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    event_channel = connection.channel()
    event_channel.queue_declare(queue='pulserr_raw')

init_rabbit()

def pulse(data):
    print("Pulse received at {}".format(data['time']))

def indentify_pulse(json_data):
    '''Consume events and identify pulses. Rise and fall in event value is a pulse'''
    global last_value
    global rising
    data = json.loads(json_data.decode("utf-8"))
    #print("Received event from sensor {} with value {} at {}".format(data['sensor'], data['value'], data['time']))
    dt = datetime.datetime.strptime( data['time'], "%Y-%m-%d %H:%M:%S.%f" )


    if last_value < data['value']:
        if not rising:
            print("\n")
        print("Rising with \t{} \t{}".format(last_value, data['value']))

        rising = True
    else:
        print("Falling with \t{} \t{}".format(last_value, data['value']))
        if rising:
            pulse(data)
        rising = False    
    last_value = data['value']

def event_callback(ch, method, properties, body):
    indentify_pulse(body)

    

event_channel.basic_consume(event_callback, queue='pulserr_raw', no_ack=True)
event_channel.start_consuming()