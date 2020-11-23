#!/usr/bin/env python
import pika
import json
import base64

image_location = "/var/www/html/image/"
device_mac_address_store = "/usr/lib/cgi-bin/mac_address"       # convert to dabase

mq_web_key = 'webQ'
mq_server_name = 'mq_server.yw.com'
mq_server_port = '5672'
default_username = 'test'   # CHANGE me or use key
default_password = 'test'   # CHANGE me or use key
credentials = pika.PlainCredentials(username=default_username, password=default_password)
connection = pika.BlockingConnection(
             pika.ConnectionParameters(host=mq_server_name, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=mq_web_key)

def callback(ch, method, properties, body):
	y = json.loads(body)

	content = y["content"]
	if(y["name"].find('.jpg') != -1):
		content = base64.b64decode(content)
	f = open(image_location + y["name"], "w")
	f.write(content)
	f.close()

	f = open(device_mac_address_store, "w")
	f.write(y["mac"])
	f.close()
	print("Received file from:  %r" % method.routing_key)

channel.basic_consume(
        queue=mq_web_key, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()
