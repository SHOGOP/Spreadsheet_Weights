from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer
import bpy
import bmesh
import numpy as np

bl_info = {
    "name": "サンプル 3-1: オブジェクトを回転するアドオン",
    "author": "ぬっち（Nutti）",
    "version": (3, 0),
    "blender": (2, 80, 0),
    "location": "3Dビューポート > Sidebar > サンプル 3-1",
    "description": "マウスの右ドラッグでオブジェクトを回転するサンプルアドオン",
    "warning": "",
    "support": "TESTING",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object",
}


class Object_Weight_Table:
    def __init__(self, object):
        if object.type == "MESH":
            self.object = object
            self.name = object.name
            self.vertex_groups = object.vertex_groups
            self.vertex = object.data.vertices
            self.vertex_count = len(object.data.vertices)
            self.colcnt = len(self.vertex_groups)
            self.rowcnt = len(self.vertex)
        else:
            self.object = object
            self.name = "NULL"
            self.vertex_groups = None
            self.vertex = None
            self.vertex_count = None
            self.colcnt = 0
            self.rowcnt = 0

    def vertex_group(self, index):
        return self.vertex_groups[index]

    def vertex_groups_name(self):
        array = []
        for idx in self.vertex_groups:
            array.append(idx.name)
        return array


class Window(QtWidgets.QWidget):
    weight_mode = "REPLACE"

    def __init__(self, parent=None, object_cls=None):
        super().__init__(parent)
        self.object_cls = object_cls
        self.tablewidget = QtWidgets.QTableWidget(object_cls.colcnt, object_cls.rowcnt)
        """ ヘッダー設定 """
        vheader = QtWidgets.QHeaderView(QtCore.Qt.Orientation.Vertical)
        vheader.ResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        vheader.setSectionsClickable(True)
        self.tablewidget.setVerticalHeader(vheader)
        hheader = QtWidgets.QHeaderView(QtCore.Qt.Orientation.Horizontal)
        hheader.ResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        hheader.setSectionsClickable(True)
        self.tablewidget.setHorizontalHeader(hheader)

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)

        self.setLayout(QtWidgets.QGridLayout())

        # Select Object Display
        self.line1 = QtWidgets.QLineEdit("object")
        self.line1.setReadOnly(True)
        self.layout().addWidget(self.line1, 0, 0)

        # wight_button generate
        self.weight_button = []
        weight_button_value = ["DELETE", "0", "5", "10", "25", "50", "75", "90", "100"]
        for i, button in enumerate(weight_button_value):
            self.weight_button.append(QtWidgets.QPushButton(str(button)))
            self.weight_button[i].setCheckable(True)
            self.layout().addWidget(self.weight_button[i], 1, i)

        self.layout().addWidget(self.tablewidget, 2, 0, 2, len(weight_button_value))

        self.set_table(object_cls)

        # ----------Event--------------
        for i, button in enumerate(self.weight_button):
            button.clicked.connect(self.clicked_weight)
        # hheader.sectionClicked.connect(self.column_select)
        # self.tablewidget=self.set_table(self.tablewidget)
        """
        self.label1 = QtWidgets.QLabel("Changing the current frame in blender updates this slider.")
        self.label2 = QtWidgets.QLabel("Changing this slider updates the current frame in blender.")
        self.slider = QtWidgets.QSlider(Qt.Horizontal)

        with bpy.context.temp_override(window=bpy.context.window_manager.windows[0]):
            self.slider.setMinimum(bpy.context.scene.frame_start)
            self.slider.setMaximum(bpy.context.scene.frame_end)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.label1)
        self.layout().addWidget(self.label2)
        self.layout().addWidget(self.slider)


        self.timer = QTimer()
        self.timer.timeout.connect(self.on_update)

        self.slider.valueChanged.connect(self.slider_changed)
        """

    def set_table(self, object_cls):
        self.line1.setText(object_cls.name)
        self.tablewidget.setColumnCount(object_cls.colcnt)
        self.tablewidget.setRowCount(object_cls.rowcnt)
        if object_cls.object == None:
            return
        Vgroups_name = object_cls.vertex_groups_name()
        self.tablewidget.setHorizontalHeaderLabels(Vgroups_name)

        count = 0
        """ テーブルの中身作成 """
        for column, group in enumerate(object_cls.vertex_groups):
            for row in range(len(object_cls.vertex)):
                try:
                    item = QtWidgets.QTableWidgetItem(
                        str(round(group.weight(row) * 100, 1))
                    )
                except RuntimeError:
                    item = QtWidgets.QTableWidgetItem("---")
                # item = QtWidgets.QTableWidgetItem("aaaa")
                self.tablewidget.setItem(row, column, item)

    def show(self):
        super(Window, self).show()
        # tick = int(1000 / 30)  # tick 1000 / frames per second
        # self.timer.start(tick)

    def column_select(self):
        self.tablewidget.selectedRanges()
        a = self.tablewidget.selectedRanges()
        print(a[0].leftColumn())
        print(a[0].rowCount())

    def on_update(self, object=None):
        self.object_cls = object
        self.set_table(object)

    def clicked_weight(self):
        object_cls = self.object_cls
        sender = self.sender()
        selected_Items = self.tablewidget.selectedItems()
        for item in selected_Items:
            idx = self.tablewidget.indexFromItem(item)
            Vgroup = object_cls.vertex_group(idx.column())
            array = []
            array.append(idx.row())
            if sender.text() == "DELETE":
                Vgroup.remove(array)
                weight = "---"
                item.setText(str(weight))
                continue
            if self.weight_mode == "ADD":
                Vgroup.add(array, abs(float(sender.text()) / 100), self.weight_mode)
                weight = round(Vgroup.weight(array[0]) * 100, 2)
            try:
                if self.weight_mode == "REPLACE":
                    Vgroup.add(array, abs(float(sender.text()) / 100), self.weight_mode)
                    weight = round(Vgroup.weight(array[0]) * 100, 2)
                if self.weight_mode == "SUBTRACT":
                    calc_weight = Vgroup.weight(idx.row()) + (
                        float(sender.text()) / 100
                    )
                    if calc_weight > 0:
                        Vgroup.add(
                            array, abs(float(sender.text()) / 100), self.weight_mode
                        )
                    else:
                        Vgroup.add(array, 0, "REPLACE")
                    weight = round(Vgroup.weight(array[0]) * 100, 2)
            except RuntimeError:
                weight = "---"
            item.setText(str(weight))

        # temp.add(test, sender.text(), "REPLACE")

        self.set_weight()

    def set_weight(self, key=None, row=0, value=0):
        pass
        # print(bpy.context.selected_objects)
        # Vertex_group = self.meshObject.vertex_groups
        # for idx in Vertex_group:
        # print(idx)

    def itemChanged(self):
        pass

    def slider_changed(self, value):
        # note that if this fails blender will crash, to prevent you can use try/except
        # bpy.context.scene.frame_set(value)
        pass
        # TODO add click support, currently it only works when you drag the slider

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        key_Message = "pressed"
        pressed = QtGui.QKeySequence(event.key()).toString(
            QtGui.QKeySequence.NativeText
        )
        if pressed == "Control":
            self.CtrKeyAction(key_Message)
        if pressed == "Shift":
            self.ShiftKeyAction(key_Message)

    def keyReleaseEvent(self, event):
        key_Message = "released"
        if event.isAutoRepeat():
            return
        released = QtGui.QKeySequence(event.key()).toString(
            QtGui.QKeySequence.NativeText
        )
        if released == "Control":
            self.CtrKeyAction(key_Message)
        if released == "Shift":
            self.ShiftKeyAction(key_Message)

    def CtrKeyAction(self, state):
        if state == "pressed":
            self.weight_mode = "ADD"
            for i, button in enumerate(self.weight_button):
                button.setText("+" + button.text())
        if state == "released":
            self.weight_mode = "REPLACE"
            for i, button in enumerate(self.weight_button):
                button.setText(button.text()[1:])

    def ShiftKeyAction(self, state):
        if state == "pressed":
            self.weight_mode = "SUBTRACT"
            for i, button in enumerate(self.weight_button):
                button.setText("-" + button.text())
        if state == "released":
            self.weight_mode = "REPLACE"
            for i, button in enumerate(self.weight_button):
                button.setText(button.text()[1:])


class UI_Interface(Window):
    pass


# マウスドラッグでオブジェクトを回転するオペレータ
class SpreadSheet_OT_Weights(bpy.types.Operator):
    bl_idname = "object.sample31_rotate_object_by_mouse_dragging"
    bl_label = "オブジェクトを回転"
    bl_description = "マウスドラッグでオブジェクトを回転します"

    # Trueの場合は、マウスをドラッグさせたときに、アクティブなオブジェクトが
    # 回転する（Trueの場合は、モーダルモード中である）
    __running = False
    # マウスが右クリックされている間に、Trueとなる
    __right_mouse_down = False

    main_window = QtWidgets.QApplication.instance().blender_widget

    w = None

    # モーダルモード中はTrueを返す
    @classmethod
    def is_running(cls):
        return cls.__running

    def modal(self, context, event):
        op_cls = SpreadSheet_OT_Weights

        # エリアを再描画
        if context.area:
            context.area.tag_redraw()

        if context.active_object.type == "MESH":
            object_class = Object_Weight_Table(context.active_object)
            self.w.on_update(object_class)

        # パネル [マウスドラッグでオブジェクトを回転] のボタン [終了] を
        # 押したときに、モーダルモードを終了
        if not self.is_running():
            return {"FINISHED"}

        """
        # マウスのクリック状態を更新
        if event.type == 'RIGHTMOUSE':
            # 右ボタンを押されたとき
            if event.value == 'PRESS':
                op_cls.__right_mouse_down = True
                op_cls.__initial_rotation_x = active_obj.rotation_euler[0]
                op_cls.__initial_mouse_x = event.mouse_region_x
            # 右ボタンが離されたとき
            elif event.value == 'RELEASE':
                op_cls.__right_mouse_down = False
                op_cls.__initial_rotation_x = None
                op_cls.__initial_mouse_x = None
            return {'RUNNING_MODAL'}
        # マウスドラッグによるオブジェクト回転
        elif event.type == 'MOUSEMOVE':
            if op_cls.__right_mouse_down:
                rotate_angle_x = (event.mouse_region_x - op_cls.__initial_mouse_x) * 0.01
                active_obj.rotation_euler[0] = op_cls.__initial_rotation_x + rotate_angle_x
                return {'RUNNING_MODAL'}
        """
        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        op_cls = SpreadSheet_OT_Weights

        if context.area.type == "VIEW_3D":
            # [開始] ボタンが押された時の処理
            if not self.is_running():
                self.Open_UI()
                op_cls.__right_mouse_down = False
                op_cls.__initial_rotation = None
                op_cls.__initial_mouse_x = None
                # モーダルモードを開始
                context.window_manager.modal_handler_add(self)
                op_cls.__running = True
                print("サンプル 3-1: オブジェクトの回転処理を開始しました。")
                return {"RUNNING_MODAL"}
            # [終了] ボタンが押された時の処理
            else:
                op_cls.__running = False
                print("サンプル 3-1: オブジェクトの回転処理を終了しました。")
                return {"FINISHED"}
        else:
            return {"CANCELLED"}

    def Open_UI(self):
        object_class = Object_Weight_Table(bpy.context.active_object)
        self.w = Window(self.main_window, object_class)
        self.w.resize(500, 500)
        self.w.show()


# UI
class SpreadSheet_PT_Weights(bpy.types.Panel):
    bl_label = "オブジェクトを回転"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "サンプル 3-1"
    bl_context = "objectmode"

    def draw(self, context):
        op_cls = SpreadSheet_OT_Weights

        layout = self.layout
        # [開始] / [終了] ボタンを追加
        if not op_cls.is_running():
            layout.operator(op_cls.bl_idname, text="開始", icon="PLAY")
        else:
            layout.operator(op_cls.bl_idname, text="終了", icon="PAUSE")


classes = [
    SpreadSheet_OT_Weights,
    SpreadSheet_PT_Weights,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    print("サンプル 3-1: アドオン『サンプル 3-1』が有効化されました。")


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    print("サンプル 3-1: アドオン『サンプル 3-1』が無効化されました。")


"""
def main():
    main_window = QtWidgets.QApplication.instance().blender_widget
    w = Window(main_window)
    w.show()
    return w
"""

if __name__ == "__main__":
    register()

    # main()
