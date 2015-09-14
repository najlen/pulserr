
'''Module to keep common rabbitmq operations'''

import pika

def init_rabbit_w_pulse_callback(pulse_callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='pulse', type='fanout')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='pulse', queue=queue_name)
    channel.basic_consume(pulse_callback, queue=queue_name, no_ack=True)
    return channel