#!/usr/bin/env python3

"""
Consume events from phidgets sensors and submit to rabbit mq queus
Code taken from the phidgets public examples"""

__author__ = 'Daniel Nihlen'
__version__ = '0.1'
__date__ = '2015-09-08'

#Basic imports
from ctypes import *
import sys
import random
from pprint import pprint as pp

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.InterfaceKit import InterfaceKit
from Phidgets.Phidget import PhidgetLogLevel

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


#Information Display Function
def displayDeviceInfo(interfaceKit):
    print("|------------|----------------------------------|--------------|------------|")
    print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    print("|------------|----------------------------------|--------------|------------|")
    print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (interfaceKit.isAttached(), interfaceKit.getDeviceName(), interfaceKit.getSerialNum(), interfaceKit.getDeviceVersion()))
    print("|------------|----------------------------------|--------------|------------|")
    print("Number of Digital Inputs: %i" % (interfaceKit.getInputCount()))
    print("Number of Digital Outputs: %i" % (interfaceKit.getOutputCount()))
    print("Number of Sensor Inputs: %i" % (interfaceKit.getSensorCount()))



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
    print("InterfaceKit {}: Sensor {}: {}".format(source.getSerialNum(), e.index, e.value))

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
    else:
        displayDeviceInfo(interfaceKit)


def setRate(interfaceKit):
    for i in range(interfaceKit.getSensorCount()):
        try:
            print("rate for sensor {} is {}".format(i, interfaceKit.getDataRate(i)))
            interfaceKit.setDataRate(i, 4)
            print("rate is {}".format(interfaceKit.getDataRate(i)))
        except PhidgetException as e:
            print("Phidget Exception {}: {}".format(e.code, e.details))
    
def main():
    interfaceKit = create_intefracekit()
    setHandlers(interfaceKit)
    openPhidget(interfaceKit)
    attachPhidget(interfaceKit)
    setRate(interfaceKit)

    #wait for input from user to close program.
    chr = sys.stdin.read(1)
    
    try:
        interfaceKit.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    
    print("Done.")
    exit(0)
main()
