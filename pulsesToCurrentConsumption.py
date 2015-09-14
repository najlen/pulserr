#!/usr/bin/env python3

"""
Consume pulses and calculate the current power consumption based on difference in timestamps.
"""
import rabbitUtils
from pprint import pprint as pp
import json
import datetime
import requests
import yaml

USE_GECKO = True

last_time_stamp = datetime.datetime.now()
last = 1.0

def calc_consumption(body):
    '''Based on the diff in time stamps, judge how much current power consumption is'''
    data = json.loads(body.decode("utf-8"))
    curr_time = datetime.datetime.strptime( data['time'], "%Y-%m-%d %H:%M:%S.%f" )
    global last_time_stamp    
    delta_time = curr_time - last_time_stamp
    delta_time_sec = delta_time.seconds + delta_time.microseconds/1000000.0
    kw = 3.6/delta_time_sec
    last_time_stamp = curr_time
    if USE_GECKO
        post_to_gecko(round(kw,1))


def post_to_gecko(value):
    global last
    diff_percent = round(abs(last - value)/last*100,0)
    print("Got value {}".format(value))
    if diff_percent > 10:
        print("Post to gecko {}".format(value))
        body = '{"api_key": "","data": {"item": 4,"min": {"value": 0},"max": {"value": 10}}}'
        json_body = json.loads(body)
        json_body['data']['item'] = value
        json_body['api_key'] =  cfg['gecko']['api_key']
        r = requests.post(cfg['gecko']['url'], json=json_body)
        r.raise_for_status()
        last = value
    
    
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
    channel.start_consuming()
main()

