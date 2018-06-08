import queue
import sys
import cv2
import numpy as np
import time
import os
import io
import logging
from celery import Celery
from logging.handlers import RotatingFileHandler
from flask import Flask, request, Response
import jsonpickle
import base64
from PIL import Image

#global flask and celery implementation
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'amqp://yliu:yliu@localhost:5672/yliu_celery_host'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

#global queue
q = queue.Queue()


@celery.task
def do_work(item):
    print('Image shape is {}, Image name is {}'.format(item[0].shape,item[1]),file=sys.stderr)
    time.sleep(1)

@app.route('/cfdserver/exfeature', methods=['POST'])
def exfeature():
    global q
    r=request.form
    #decode image file
    encoded_data = r['img']
    img_data = base64.b64decode(str(encoded_data))
    image = Image.open(io.BytesIO(img_data))
    img = cv2.cvtColor(np.array(image), cv2.IMREAD_COLOR)

    keyname = r['keyname']

    item = (img,keyname)
    q.put(item)

    print('Current queue length is %d'%(q.qsize()),file=sys.stdout) 

    do_work(item)
    response = {'message': 'image received. size={}'.format(img.shape),'device':keyname}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
    '''
    im_name_list = os.listdir(im_path)
    
    for im_file in im_name_list:
        im_complete_file = os.path.join(im_path,im_file)
        item = (cv2.imread(im_complete_file),im_file)
        q.put(item)
    '''
    # block until all tasks are done
    q.join()
