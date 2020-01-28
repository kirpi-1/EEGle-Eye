import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('10.0.0.12:5672'))

channel = connection.channel()

channel.queue_declare(queue='hello')
