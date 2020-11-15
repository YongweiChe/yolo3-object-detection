#!/usr/bin/env python
import pika
import json
import base64
import script

###
#parameterize: routing_key: queue
###


credentials = pika.PlainCredentials(username='test', password='test')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='mq_server.yw.com', credentials=credentials))
channel = connection.channel()


channel.queue_declare(queue='queue1')

def callback(ch, method, properties, body):
    y = json.loads(body)
    content = y["content"]
    name = y["name"]
 
    print("received name is: %s" % name)

    if(name.find('.jpg') != -1):
        content = base64.b64decode(content)
        print("in here1")
        f = open("raw_image.jpg", "bw")
        f.write(content)
        f.close()
        script.detect('raw_image.jpg', 'yolov3.cfg', 'yolov3.weights', 'human.txt', ["cat"])
        detected_image_json = script.picture_to_json('detected-object.jpg', name)
        script.send(detected_image_json, 'mq_server.yw.com', mq_server_port="5672", username="test", password="test", routing_key="yolo_queue") 
    else:
        script.send(body, 'mq_server.yw.com', mq_server_port="5672", username="test", password="test", routing_key="yolo_queue") 
    print("Received %r" % method.routing_key)
     
  
channel.basic_consume(
    queue='queue1', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
