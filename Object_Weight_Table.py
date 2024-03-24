from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer, QModelIndex, QAbstractTableModel
import bpy
import bmesh
import numpy as np


from . import util


class Object_Weight_Table(QAbstractTableModel):
    def __init__(self, object, parent=None):
        super().__init__(parent)
        if object != None:
            if object.type == "MESH":
                self.object = object
                self.name = object.name
                self.vertex_groups = object.vertex_groups
                self.vertex = object.data.vertices
                self.vertex_count = len(object.data.vertices)
                self.select_vertex = []
                self.select_vertex_count = 0
                for idx in object.data.vertices:
                    self.select_vertex.append(idx.select)
                for idx in self.select_vertex:
                    if idx:
                        self.select_vertex_count += 1
                self.colcnt = len(self.vertex_groups)
                self.rowcnt = len(self.vertex)
                return
        self.object = object
        self.name = "NULL"
        self.vertex_groups = None
        self.vertex = None
        self.vertex_count = None
        self.select_vertex = []
        self.select_vertex_count = 0
        self.colcnt = 0
        self.rowcnt = 0

    # 指定したインデックスの頂点グループを返す
    def vertex_group(self, index):
        return self.vertex_groups[index]

    def get_vertex_group_index(self, name):
        for i, idx in enumerate(self.vertex_groups):
            if idx.name == name:
                return i
        else:
            return -1

    # 頂点グループ名の一覧を返す
    def vertex_groups_name(self):
        array = []
        if self.vertex_groups == None:
            return array
        for idx in self.vertex_groups:
            array.append(idx.name)
        return array

    def all_select_vertex(self):
        for i, idx in enumerate(self.select_vertex):
            self.select_vertex[i] = True
        self.select_vertex_count = len(self.select_vertex)

    """
    def mirror_vertex_group(self):
        self.object.vertex_group_mirror(mirror_weights=True)
    """
