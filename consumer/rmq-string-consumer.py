import pika
import numpy as np
import os
import sys, signal

def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def nparray_callback(ch, method, props, body):
	print(body)


rmquser = os.environ['RABBITMQ_USERNAME']
rmqpass = os.environ['RABBITMQ_PASSWORD']
queue = "stringout"
credentials = pika.PlainCredentials(rmquser,rmqpass)

connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.12',credentials=credentials))
channel = connection.channel()

channel.basic_consume(queue=queue, on_message_callback=nparray_callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()




