#! /usr/bin/env python3
# -*- encoding: utf-8 -*-
"""
app.py
python カメラモジュール操作のデーモン
"""
__author__ = 'Yoshiya Ito <myon53@gmail.com>'
__version__ = '0.0.1'
__date__ = '16 Nov 2015'

import threading
import io
import time
import picamera
import tornado
import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.ioloop

class HTTP(tornado.web.RequestHandler):
    def get(self):
        self.render('./index.html');


class WS(tornado.websocket.WebSocketHandler):

    def initialize(self):
        camera = picamera.PiCamera()
        camera.resolution = (450, 300)
        camera.framerate = 30
        camera.stream = io.BytesIO()
        time.sleep(2)
        self.camera = camera

    def open(self):
        print('{0}:connection open'.format(self.request.remote_ip))
        t = threading.Thread(target=self.rec)
        t.setDaemon(True)
        t.start()

    def rec(self):
        for _ in self.camera.capture_continuous(self.camera.stream, 'jpg', use_video_port=True):
            self.camera.stream.seek(0)
            self.write_message(self.camera.stream.read(), binary=True)
            self.camera.stream.seek(0)
            self.camera.stream.truncate()
            if not self.state:
                break

    def on_close(self):
        self.status = False
        self.close()
        print('{0}:connection close'.format(self.request.remote_ip))

if __name__ == '__main__':

    app = tornado.web.Application([
        ('/', HTTP),
        ('/live', WS)
    ]);
    http = tornado.httpserver.HTTPServer(app);
    http.listen(5000)
    tornado.ioloop.IOLoop.instance().start();
