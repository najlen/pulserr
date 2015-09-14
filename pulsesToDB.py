#!/usr/bin/env python3

"""
Consume pulses and store counter to db.
"""

import pika
import sqlite3 as lite
from pprint import pprint as pp
import rabbitUtils

#Global db connection
global con

def pulse_callback(ch, method, properties, body):
    print("Pulse received: {}".format(body))
    store_pulse_to_db()

def store_pulse_to_db():
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO counters (date, cnt) VALUES (DATE(),0);") 
    cur.execute('UPDATE counters set cnt = cnt +1 where date LIKE DATE();') 
    
def init_lite():
    '''Init sqlite3 db'''    
    global con
    con = None
    try:
        con = lite.connect("{}.sqlite".format(__file__[:-3]), isolation_level=None)    
        cur = con.cursor()    
        cur.execute("CREATE TABLE if not exists currentpow (id INTEGER PRIMARY KEY, value FLOAT);")
        cur.execute("CREATE TABLE if not exists counters (`date` date NOT NULL, `cnt` int NOT NULL, PRIMARY KEY (`date`));")
        cur.execute("INSERT OR IGNORE into currentpow (id, value) values (1, 0.0);")
        
    except lite.Error as e:
        print("Error %{}:".format(e.args[0]))
        sys.exit(1)
    
    return con   
    
    
def main():
    con = init_lite()
    channel = rabbitUtils.init_rabbit_w_pulse_callback(pulse_callback)
    
    #Blocking call, will wait for callbacks.
    channel.start_consuming()
    
main()

