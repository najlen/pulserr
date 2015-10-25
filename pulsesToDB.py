#!/usr/bin/env python3

"""
Consume pulses and store counter to db.
"""

import pika, rabbitUtils, dateutil.parser, json
import sqlite3 as lite

#Global db connection
global con

def pulse_callback(ch, method, properties, body):
    print("Pulse received: {}".format(body))
    store_pulse_to_db(body)

def store_pulse_to_db(body):
    data = json.loads(body.decode("utf-8"))
    date_time = dateutil.parser.parse(data['time'])
    day_string = "{:%Y-%m-%d}".format(date_time)
    minute_string = "{:%Y-%m-%d %H:%M}".format(date_time)
    print(minute_string)
    cur = con.cursor()

    cur.execute("INSERT OR IGNORE INTO counters_day (date, cnt) VALUES (\'{}\',0);".format(day_string)) 
    cur.execute("INSERT OR IGNORE INTO counters_minute (date, cnt) VALUES (\'{}\',0);".format(minute_string)) 

    cur.execute('UPDATE counters_day set cnt = cnt +1 where date LIKE \'{}\';'.format(day_string)) 
    cur.execute("UPDATE counters_minute set cnt = cnt +1 where date LIKE \'{}\';".format(minute_string)) 
    
def init_lite():
    '''Init sqlite3 db'''    
    global con
    con = None
    try:
        con = lite.connect("{}.sqlite".format(__file__[:-3]), isolation_level=None)    
        cur = con.cursor()    
        cur.execute("CREATE TABLE if not exists currentpow (id INTEGER PRIMARY KEY, value FLOAT);")
        cur.execute("CREATE TABLE if not exists counters_day (`date` date NOT NULL, `cnt` int NOT NULL, PRIMARY KEY (`date`));")
        cur.execute("CREATE TABLE if not exists counters_minute (`date` date NOT NULL, `cnt` int NOT NULL, PRIMARY KEY (`date`));")        
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

