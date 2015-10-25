#!/usr/bin/env python3

"""
Consume pulses and calculate the current power consumption based on difference in timestamps.
"""

from pprint import pprint as pp
from datetime import datetime 
from datetime import timedelta 
import json, requests, yaml, sys, time, rabbitUtils, dateutil.parser
import sqlite3 as lite

USE_GECKO = True

last_time_stamp = datetime.now()
last = 1.0

def init_lite():
    '''Init sqlite3 db'''    
    global con
    
    con = None
    try:
        con = lite.connect("pulsesToDB.sqlite", isolation_level=None)    
            
    except lite.Error as e:
        print("Error {}:".format(e.args[0]))
        sys.exit(1)
    
    return con   

def calc_consumption(body):
    '''Based on the diff in time stamps, judge how much current power consumption is'''
    data = json.loads(body.decode("utf-8"))
    curr_time = dateutil.parser.parse(data['time'])
    global last_time_stamp    
    delta_time = curr_time - last_time_stamp
    delta_time_sec = delta_time.seconds + delta_time.microseconds/1000000.0
    kw = 3.6/delta_time_sec
    last_time_stamp = curr_time
    if USE_GECKO:
        post_to_gecko(round(kw,1))


def post_to_gecko_meter(value):
    body = '{"api_key": "","data": {"item": 4,"min": {"value": 0},"max": {"value": 10}}}'
    json_body = json.loads(body)
    json_body['data']['item'] = value
    json_body['api_key'] =  cfg['gecko_meter']['api_key']
    r = requests.post(cfg['gecko_meter']['url'], json=json_body)
    
def post_to_gecko_num(value):
    body = {'api_key': cfg['gecko_num']['api_key'], 'data': {'item': [{ 'value': value }]}}
    req = requests.Request('POST',cfg['gecko_num']['url'], json=body)
    r = requests.post(cfg['gecko_num']['url'], json=body)


def post_to_gecko(value):
    global last
    diff_percent = round(abs(last - value)/last*100,0)
    print("Got value {}".format(value))

    #Only post when significant changes occours to avoid posting all the time
    if diff_percent > 10:
        print("Post to gecko {}".format(value))
        post_to_gecko_meter(value)
        post_to_gecko_num(value)


        last = value
    sys.stdout.flush()
    
    
    
def pulse_callback(ch, method, properties, body):
    calc_consumption(body)
    

def load_config():
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg    


def main():
    channel = rabbitUtils.init_rabbit_w_pulse_callback(pulse_callback)
    #Blocking call, will wait for callbacks.
    global cfg
    cfg = load_config()
    init_lite()
    channel.start_consuming()



main()

