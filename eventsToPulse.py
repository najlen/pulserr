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

global channel

def init_rabbit():
    global channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='pulse', type='fanout')
    channel.queue_declare(queue='pulserr_raw')
    #channel.queue_declare(queue='pulserr_pulse')


def pulse(data):
    print("Pulse received at {}".format(data['time']))
    body = "{{\
    \"time\" : \"{}\",\
    \"sensor\": {}}}".format(data['time'], data['sensor'])
    print(body)
    #channel.basic_publish(exchange='', routing_key='pulserr_pulse', body=body)
    channel.basic_publish(exchange='pulse', routing_key='', body=body)

def indentify_pulse(json_data):
    '''Consume events and identify pulses. Rise and fall in event value is a pulse'''
    global last_value
    global rising
    data = json.loads(json_data.decode("utf-8"))
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

def main():
    init_rabbit()
    channel.basic_consume(event_callback, queue='pulserr_raw', no_ack=True)
    channel.start_consuming()
        
main()