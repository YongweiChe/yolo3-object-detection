#!/usr/bin/env python
import pika
import json
import base64

# some fix strings for testing
image_path = "/var/yolo_image/"
msg_queue_key = 'sensorQ'

# yes not secure for inital concert proving. Password should read from vault or somewhere. 
credentials = pika.PlainCredentials(username='test', password='test')
connection = pika.BlockingConnection(
             pika.ConnectionParameters(host='mq_server.yw.com', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=msg_queue_key)

#
def callback(ch, method, properties, body):
  y = json.loads(body)
  content = y["content"]
  if(y["name"].find('.jpg') != -1):
    content = base64.b64decode(content)
    image_name = image_path + y["name"]
    f = open(image_name, "w")
    f.write(content)
    f.close()
    print("Received from RabbitMQ: %s, image name: %s" % (method.routing_key, image_name))

channel.basic_consume(
        queue=msg_queue_key, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
