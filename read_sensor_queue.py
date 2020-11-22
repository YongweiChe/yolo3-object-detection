#!/usr/bin/env python
import pika
import json
import base64
import script

image_path = "./yolo_image/"
msg_queue_key = 'sensorQ'
credentials = pika.PlainCredentials(username='test', password='test')
connection = pika.BlockingConnection(
             pika.ConnectionParameters(host='mq_server.yw.com', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=msg_queue_key)

def callback(ch, method, properties, body):
  y = json.loads(body)
  content = y["content"]
  if(y["name"].find('.jpg') != -1):
    content = base64.b64decode(content)
    image_name = image_path + y["name"]
    f = open(image_name, "bw")
    f.write(content)
    f.close()
    print("Received from RabbitMQ: %s, image name: %s" % (method.routing_key, image_name))

    script.detect(image_name, 'yolov3.cfg', 'yolov3.weights', 'human.txt', ["cat"])
    detected_image_json = script.picture_to_json('detected-object.jpg', image_name)
    script.send(detected_image_json, 'mq_server.yw.com', mq_server_port="5672", username="test", password="test", routing_key="yolo_queue")
  else:
    script.send(body, 'mq_server.yw.com', mq_server_port="5672", username="test", password="test", routing_key="yolo_queue")

channel.basic_consume(
        queue=msg_queue_key, on_message_callback=callback, auto_ack=True)

channel.basic_consume(
        queue=msg_queue_key, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
