from threading import Thread, Event
import time
import cv2
import numpy as np
import os
class new_camera(Thread):
    def __init__(self,config, **kargs):
        Thread.__init__(self)
        self.config = config
        self.name = self.config["name"]
        self.id = self.config["usbid"]
        self.frame = self.backGround() if isinstance(kargs.get("background"), type(None))  else kargs.get("background")
        self.cam = cv2.VideoCapture(self.id)
        self._stop_event = Event()
        self.runnig = Event()
        
    def backGround(self, h=600, w=900, c=0):
        bgk = np.zeros([h, w, 3], np.uint8)
        bgk[:, :, c] = np.zeros([h, w]) + 255
        return bgk

    def stop(self):
        self.runnig.clear()
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def isRunning(self):
        return (self.cam.isOpened() and not self.stopped())
    
    def awaitStart(self, timeout):
        t0 = time.monotonic() + timeout
        # print(self.isRunning())
        while time.monotonic() < t0:
            pass
        return None

    def close(self):
        self.stop()
        self.cam.release()
        cv2.destroyAllWindows()

    def setProperties(self, dict):
        for name, value in dict["properties"].items():
            self.setPropertie(name, value)

    def getProperties(self, dict):
        props = {}
        for name, value in dict["properties"].items():
            props[name] = self.getPropertie(name)

    def getPropertie(self, name):
        return self.cam.get(getattr(cv2, self.config["prefix"]+name))

    def setPropertie(self, name, value):
        self.cam.set(getattr(cv2, self.config["prefix"]+name), value)

    def run(self):
        self.camera()
    
    def getFrame(self):
        return self.frame

    def camera(self):
        self.setProperties(self.config)
        _ = True
        while self.isRunning() and _:
            _, self.frame = self.cam.read()
        self.stop()
        self.close()
    
    def stream(self):
        while self.isRunning():
            frame = self.getFrame()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
                       + cv2.imencode('.JPEG', frame,
                                      [cv2.IMWRITE_JPEG_QUALITY, 100])[1].tobytes()
                       + b'\r\n')


class Identify(object):
    def __init__(self, cameraThread, function, config):
        self.function = function
        self.config = config
        self.cam = cameraThread

    def identify(self):
        return self.function(self.cam.getFrame(), self.config)

    

if __name__ == '__main__':
    cam = new_camera(config={"prefix":"CAP_PROP_", "suffix":"", "properties":{}})
    cam.start()
    while cam.isRunning() and cv2.waitKey(1) != 27:
        cv2.imshow("frame", cam.getFrame())
    else:
        cam.close()
        cam.join()      
    print("ok")