from cv2 import calibrateCamera, createTrackbar, namedWindow, getTrackbarPos, resizeWindow, subtract
from numpy import array
import numexpr as ne
import numpy as np
import cv2
import colorsys
from ..util import color

def createWindow(config):
    def empty(a):
        pass
    namedWindow(config["windowName"])
    resizeWindow(config["windowName"], config["windowSize"][0], config["windowSize"][1])
    for item in config["Trackbars"]:
        for name in item["names"]:
            for sfx in item["suffix"]:
                createTrackbar(f"{name}{sfx}", config["windowName"], item["values"][0], item["values"][1], empty)


def getWindow(config):
    values={}
    for item in config["Trackbars"]:
        for name in item["names"]:
            for sfx in item["suffix"]:
                values[f"{name}{sfx}"] = getTrackbarPos(f"{name}{sfx}", config["windowName"])
    return values
