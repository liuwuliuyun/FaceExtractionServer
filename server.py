import sys
import cv2
import numpy as np
import time
import os
import io
import logging
import tensorflow as tf
import time
import random
import base64
import jsonpickle
import zmq
from threading import Lock
from flask import Flask, request, Response
from PIL import Image
from ext.extractor import extractor
from ext.aligner import aligner

#global flask and celery implementation
app = Flask(__name__)

context = zmq.Context()
zmq_socket = context.socket(zmq.PUSH)
zmq_socket.bind("tcp://127.0.0.1:5557")

lock = Lock()

@app.route('/cfdserver/exfeature', methods=['POST'])
def exfeature():
    global channel
    r=request.form
    #decode image file
    encoded_data = r['img']
    keyname = r['keyname']
    encoded_data = keyname + encoded_data
    #TODO check queue length before publish
    #TODO send keyname with image
    with lock:
        zmq_socket.send_string(encoded_data)
    #TODO discard new image if queue is full
    response = {'message': 'image received successful', 'device':keyname}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")
    

if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
    app.run(host="0.0.0.0",port=5000,threaded=True)
