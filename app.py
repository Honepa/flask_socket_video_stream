import time
import psutil
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import cv2
import base64
from datetime import datetime

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

 
def background_thread():
    cap=cv2.VideoCapture(0)
    while(cap.isOpened()):
        ret,img=cap.read()
        if ret:
            date = datetime.now()
            frame = cv2.putText(img, date.isoformat(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 0, 0), 2, cv2.LINE_AA)
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            frame= base64.encodebytes(frame).decode("utf-8")
            socketio.emit('server_response',
                          json.dumps({'image': frame, 'answer': date.isoformat()}),
                          namespace='/test')
            socketio.sleep(0.03)
        else:
            break
 
 
@app.route('/')
def index():
    return render_template('index.html')#, async_mode=socketio.async_mode)
 
 
@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
 
 
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)