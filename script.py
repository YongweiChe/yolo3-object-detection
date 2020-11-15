#############################################
# Object detection - YOLO - OpenCV
# Author : Arun Ponnusamy   (July 16, 2018)
# Website : http://www.arunponnusamy.com
############################################
###!/home/pi/env/bin/python
#!/bin/env python
import cv2
import argparse
import numpy as np
import pika
import json
import base64
import netifaces

def send(json_document, mq_server, mq_server_port="5672", username="test", password="test", routing_key="yolo_queue"):
    credentials = pika.PlainCredentials(username=username, password=password)
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=mq_server, port=mq_server_port, credentials=credentials))

    channel = connection.channel()

    channel.queue_declare(queue=routing_key)

    channel.basic_publish(exchange='', routing_key= routing_key, body= json_document)
    print(" [x] Sent ")
    connection.close()

def picture_to_json(detected_image_name, original_image_name):
    f = open(detected_image_name, "rb")
    content = f.read()
    f.close()
    mac_address = "123445678z"
    msg = base64.b64encode(content).decode("utf-8")
    # a Python object (dict):
    x = {"name": original_image_name, "content": msg, "mac": mac_address}
    # convert into JSON:
    y = json.dumps(x)

    # the result is a JSON string:
    return y

def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h, classes, COLORS):
   
    print(class_id)

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def detect(argsImage, argsConfig, argsWeights, argsClasses, classWanted):    
    image = cv2.imread(argsImage)
    
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    
    classes = []
    classesDict = {} 
    
    with open(argsClasses, 'r') as f:
        for i, line in enumerate(f.readlines()):
            classes.append(line.strip())
            classesDict.update({line.strip():i}) 
    print(classesDict) 
    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
    
    net = cv2.dnn.readNet(argsWeights, argsConfig)
    
    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
    
    net.setInput(blob)
    
    outs = net.forward(get_output_layers(net))
    
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    
    
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            for c in classWanted:
               if (class_id == classesDict[c]):
                   confidence = scores[class_id]
               else:
                   confidence = 0
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    
    
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    
    count = 0   
    locations = {} 
    for i in indices:
        i = i[0]
        box = boxes[i]
        x = int(box[0])
        y = int(box[1])
        w = int(box[2])
        h = int(box[3])
        if (class_ids[i] == 0):
            count = count + 1
            person = "".join(("person ",str(count)))
            locations.update( {person: (x,y,w,h)})
        if (class_ids[i] == 16):
            count = count + 1
            dog = "".join(("dog ", str(count)))
            locations.update( {dog: (x, y, w, h)})
        draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h), classes, COLORS)
    print(locations)
    cv2.imwrite("detected-object.jpg", image)
    cv2.destroyAllWindows()
    return locations

classWanted = ["dog"]
#detect('man_dog.jpeg', 'yolov3.cfg', 'yolov3.weights', 'human.txt', ["cat"])
#image_json = picture_to_json('detected-object.jpg') 
# convert into JSON:
#send(image_json,'mq_server.yw.com')

#detect(args.image, args.config, args.weights, args.classes, classWanted)
