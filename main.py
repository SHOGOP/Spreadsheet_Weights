from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer
import bpy
import bmesh
import numpy as np
import logging
import traceback


from .Object_Weight_Table import Object_Weight_Table
from .ui import Window


class StackLogger(logging.Logger):
    def _log(
        self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs
    ):
        super()._log(
            level,
            str(msg) + "\n" + "".join(traceback.format_stack()),
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            **kwargs
        )


logging.setLoggerClass(StackLogger)

w = None
main_window = QtWidgets.QApplication.instance().blender_widget


# マウスドラッグでオブジェクトを回転するオペレータ
class SpreadSheet_OT_Weights(bpy.types.Operator):
    bl_idname = "object.spreadsheet_weights"
    bl_label = "ウェイトを調整"
    bl_description = "スプレッドシート形式でウェイトを設定する"

    # Trueの場合は、マウスをドラッグさせたときに、アクティブなオブジェクトが
    # 回転する（Trueの場合は、モーダルモード中である）
    __running = False
    # マウスが右クリックされている間に、Trueとなる
    __right_mouse_down = False

    # モーダルモード中はTrueを返す
    @classmethod
    def is_running(cls):
        return cls.__running

    def modal(self, context, event):
        op_cls = SpreadSheet_OT_Weights

        # エリアを再描画
        if context.area:
            context.area.tag_redraw()
        if context.active_object == None:
            object_class = Object_Weight_Table(None)
            return {"PASS_THROUGH"}
        # print(context.active_object.type)
        if context.active_object.type == "MESH":
            object_class = Object_Weight_Table(context.active_object)
            if context.mode == "EDIT_MESH":
                context.edit_object.update_from_editmode()
                w.set_edit_mode(True)
            elif context.mode == "OBJECT":
                w.set_edit_mode(False, "OBJECT")
            else:
                w.set_edit_mode(False)
            w.on_update(object_class)

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
                print("Spreadsheet_Weights: ウィンドウを開きました")
                return {"RUNNING_MODAL"}
            # [終了] ボタンが押された時の処理
            else:
                op_cls.__running = False
                # self.w.ui_close()
                # print(self.w)
                w.ui_close()
                print("Spreadsheet_Weights: ウィンドウを閉じました")
                return {"FINISHED"}
        else:
            return {"CANCELLED"}

    def Open_UI(self):
        global main_window, w
        object_class = Object_Weight_Table(bpy.context.active_object)
        w = Window(main_window, object_class)
        w.resize(600, 600)
        w.setWindowTitle("Spread Weights")
        w.show()
        # main_window.hide()


# UI
class SpreadSheet_PT_Weights(bpy.types.Panel):
    bl_label = "Spreadsheet_Weights"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "S.Weight"
    bl_context = "objectmode"

    def draw(self, context):
        op_cls = SpreadSheet_OT_Weights

        layout = self.layout
        # [開始] / [終了] ボタンを追加
        if not op_cls.is_running():
            layout.operator(op_cls.bl_idname, text="開始", icon="PLAY")
        else:
            layout.operator(op_cls.bl_idname, text="終了", icon="PAUSE")
