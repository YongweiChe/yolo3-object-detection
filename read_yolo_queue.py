#!/usr/bin/env python
import pika
import json
import base64
import glob

html_location = "/var/www/html/"
image_folder = "image/"
image_location = html_location + image_folder
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

#
# writes html for links.html and sends it over to the web server
#

def update_past_images(html_location, image_location):
        html_file = html_location + "links.html"
        f = open(html_file, "w")
        f.write('<html>')
        counter = 0
        for image in sorted(glob.glob(image_location + '*'), reverse = True):
                #f.write('<a href = "' + image[9:] + '">Photo taken on ' + image[20:30] +' at ' + image[-9:-4] + '</a> <p> </p>')
                prefix_len = len(html_location)
                f.write('<a href = "' + image[prefix_len:] + '">' + image[prefix_len:] + '</a> <p> </p>')
                counter += 1
                if counter == 5:
                        break
        f.write('</html>')
        f.close()

def callback(ch, method, properties, body):
	y = json.loads(body)

	content = y["content"]
	if(y["name"].find('.jpg') != -1):
		content = base64.b64decode(content)
	f = open(image_location + y["name"], "w")
	f.write(content)
	f.close()

	print("Received file from:  %r" % method.routing_key)

	update_past_images(html_location, image_location)

# main
channel.basic_consume(
        queue=mq_web_key, on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

channel.start_consuming()

