from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer
import bpy
import bmesh
import numpy as np
import time

timer = 0


def normalize(
    l,
    max=1,
):
    l_convert = max / sum(l)
    return [i * l_convert for i in l]


def convert_percent(num):
    res = round(num * 100, 1)
    return res

    """
    input:[0.5, 0.06468125432729721, 0.36191245913505554]
    output:[0.5050614375728515, 0.0, 0.3448508043450667]
    """


def timer_start():
    global timer
    timer = time.time()


def timer_stop():
    global timer
    timer = time.time() - timer
    print(f"処理時間：{timer}")
