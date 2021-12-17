from threading import Thread, Event
import time
import cv2
import numpy as np
import os
class USB_Camera:
    def __init__(self, config) -> None:
        self.config = config
        self.name = self.config.get('name')
        self.stream = cv2.VideoCapture(self.config.get('usbid'))
        self.setProperties(self.config)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        pass

    def setPropertie(self, name, value):
        self.stream.set(getattr(cv2, self.config["prefix"]+name), value)
    
    def setProperties(self, dict):
        for name, value in dict["properties"].items():
            self.setPropertie(name, value)

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while not self.stopped:
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
    
    def image_stream(self):
        while not self.stopped:
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
                       + cv2.imencode('.JPEG', self.frame,
                                      [cv2.IMWRITE_JPEG_QUALITY, 100])[1].tobytes()
                       + b'\r\n')


# class Identify(object):
#     def __init__(self, cameraThread, function, config):
#         self.function = function
#         self.config = config
#         self.cam = cameraThread

#     def identify(self):
#         return self.function(self.cam.getFrame(), self.config)
