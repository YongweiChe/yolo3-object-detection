#!/usr/bin/env python
import pika
import json
import base64
import script

yolo_image = 'detected-object.jpg'
image_path = "./yolo_image/"
mq_sensor_key = 'sensorQ'
mq_web_key = 'webQ'
mq_server_name = 'mq_server.yw.com'
mq_server_port = '5672'
yolo_config = 'yolov3.cfg'
yolo_weights = 'yolov3.weights'
yolo_label = 'yolov3.label'
yolo_objects = ["cat"]

default_username = 'test'   # CHANGE me or use key
default_password = 'test'   # CHANGE me or use key

credentials = pika.PlainCredentials(username=default_username, password=default_password)
connection = pika.BlockingConnection(
             pika.ConnectionParameters(host=mq_server_name, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=mq_sensor_key)

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

    script.detect(image_name, yolo_config, yolo_weights, yolo_label, yolo_objects)
    detected_image_json = script.picture_to_json(yolo_image, image_name)
    script.send(detected_image_json, mq_server_name, mq_server_port=mq_server_port, username=default_username, password=default_password, routing_key=mq_web_key)
  else:
    script.send(body, mq_server_name, mq_server_port=mq_server_port, username=default_username, password=default_password, routing_key=mq_web_key)

channel.basic_consume(
        queue=mq_sensor_key, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
