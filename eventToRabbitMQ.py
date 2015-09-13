#!/usr/bin/env python3

"""
Consume events from phidgets sensors and submit to rabbit mq queus
Code taken from the phidgets public examples
"""

__author__ = 'Daniel Nihlen'
__version__ = '0.1'
__date__ = '2015-09-08'

#Basic imports
from ctypes import *
import sys
from pprint import pprint as pp

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit
from Phidgets.Phidget import PhidgetLogLevel

#RabbitMQ by Pika
import pika
import datetime


def create_intefracekit():
    print("create_intefacekit")
    #Create an interfacekit object
    try:
        interfaceKit = InterfaceKit()
    except RuntimeError as e:
        print("Runtime Exception: {}".format(e.details))
        print("Exiting.")
        raise
        #exit(1)
    return interfaceKit


## RabbitMQ functions
def initRabbit():
    global channel
    global connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='pulserr_raw')

def sendRabbitMessage(sensor, value):
    body = "{{\
    \"time\" : \"{}\",\
    \"sensor\": {},\
    \"value\" : {}}}".format(datetime.datetime.now(), sensor, value)
    print(body)
    channel.basic_publish(exchange='', routing_key='pulserr_raw', body=body)

#Event Handler Callback Functions
def interfaceKitAttached(e):
    attached = e.device
    print("InterfaceKit {} Attached!".format(attached.getSerialNum()))

def interfaceKitDetached(e):
    detached = e.device
    print("InterfaceKit {} Detached!".format(detached.getSerialNum()))

def interfaceKitError(e):
    try:
        source = e.device
        print("InterfaceKit {}: Phidget Error {}: {}".format(source.getSerialNum(), e.eCode, e.description))
    except PhidgetException as e:
        print("Phidget Exception {}: {}".format(e.code, e.details))

def interfaceKitInputChanged(e):
    source = e.device
    print("InterfaceKit {}: Input {}: {}".format(source.getSerialNum(), e.index, e.state))

def interfaceKitSensorChanged(e):
    source = e.device
    sendRabbitMessage(e.index, e.value)

def interfaceKitOutputChanged(e):
    source = e.device
    print("InterfaceKit {}: Output {}: {}".format(source.getSerialNum(), e.index, e.state))

def setHandlers(interfaceKit): 
    try:
        interfaceKit.setOnAttachHandler(interfaceKitAttached)
        interfaceKit.setOnDetachHandler(interfaceKitDetached)
        interfaceKit.setOnErrorhandler(interfaceKitError)
        interfaceKit.setOnInputChangeHandler(interfaceKitInputChanged)
        interfaceKit.setOnOutputChangeHandler(interfaceKitOutputChanged)
        interfaceKit.setOnSensorChangeHandler(interfaceKitSensorChanged)
    except PhidgetException as e:
        print("Phidget Exception {}: {}".format(e.code, e.details))
        raise
    
def openPhidget(interfaceKit):    
    try:
        interfaceKit.openPhidget()
    except PhidgetException as e:
        print("Phidget Exception {%i}: {%s}".format(e.code, e.details))
        raise()


def attachPhidget(interfaceKit):
    try:
        interfaceKit.waitForAttach(5000)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        try:
            interfaceKit.closePhidget()
        except PhidgetException as e:
            print("Phidget Exception {}: {}".format(e.code, e.details))
            exit(1)
        exit(1)



def setRate(interfaceKit):
    ik = interfaceKit
    for i in range(interfaceKit.getSensorCount()):
        print("setRate for {}".format(i))
        try:
            interfaceKit.setDataRate(i, 16)
            print("rate is {}".format(interfaceKit.getDataRate(i)))
        except PhidgetException as e:
            print("Phidget Exception {}: {}".format(e.code, e.details))
            raise
        
def setChangeTrigger(interfaceKit):
    for i in range(interfaceKit.getSensorCount()):
        try:
            interfaceKit.setSensorChangeTrigger(i,2)
        except PhidgetException as e:
            print("Phidget Exception {}: {}".format(e.code, e.details))    
    
def closeInterfacekit(interfaceKit):
    try:
        interfaceKit.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception {}: {}".format(e.code, e.details))
        exit(1)
    



def main():
    initRabbit()
    interfaceKit = create_intefracekit()
    setHandlers(interfaceKit)
    openPhidget(interfaceKit)
    attachPhidget(interfaceKit)
    setChangeTrigger(interfaceKit)
    setRate(interfaceKit)

    #wait for input from user to close program.
    chr = sys.stdin.read(1)
    interfaceKit.closePhidget()
    connection.close()
        
    exit(0)
main()
