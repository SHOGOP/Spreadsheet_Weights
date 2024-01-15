from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer
import bpy
import bmesh
import numpy as np
from . import util
import sys
import logging
import traceback

logger = logging.getLogger(__name__)

logger.debug(...)


class Window(QtWidgets.QWidget):
    weight_mode = "REPLACE"
    normalize_mode = False
    edit_mode_toggle = False
    hilight_mode = False
    focus_mode = False
    item_clicked = False
    weight_button_clicked = False
    vertex_mirror_flag = False
    show_all_mode = False
    slider_press = False
    item_press = False
    select_button_click = False
    multi_change = False

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

        # オブジェクト名表示
        ui_row = 0
        self.line1 = QtWidgets.QLineEdit("object")
        self.line1.setReadOnly(True)
        self.line1.setFixedSize(100, 25)
        self.layout().addWidget(self.line1, ui_row, 0)

        self.mode_button = []
        mode_button_value = ["ShowAll:OFF", "Hilight:OFF", "Focus:OFF", "Mirror"]
        # モードボタン配置

        for i, button in enumerate(mode_button_value):
            self.mode_button.append(QtWidgets.QPushButton(str(button)))
            self.mode_button[i].setCheckable(True)
            self.layout().addWidget(self.mode_button[i], ui_row, i + 1)

        # ウェイトボタン生成
        ui_row = 1

        self.weight_button = []
        weight_button_value = [
            "AutoNormalize:OFF",
            "0",
            "5",
            "10",
            "25",
            "50",
            "75",
            "90",
            "100",
            "DELETE",
        ]
        # ウェイトボタン配置
        for i, button in enumerate(weight_button_value):
            self.weight_button.append(QtWidgets.QPushButton(str(button)))
            self.weight_button[i].setCheckable(True)
            self.layout().addWidget(self.weight_button[i], ui_row, i)
        # スライダー関連
        ui_row = 2
        self.line2 = QtWidgets.QLineEdit("0.0")
        self.line2.setFixedSize(50, 25)

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)

        self.layout().addWidget(self.line2, ui_row, 0)
        self.layout().addWidget(self.slider, ui_row, 1, 1, len(weight_button_value) - 2)
        # フィルター関連
        ui_row = 3

        self.select_button = QtWidgets.QPushButton("SELECT")
        self.select_button.setCheckable(True)
        self.filter_label1 = QtWidgets.QLabel("WeightFilter:")
        self.weight_filter_line = QtWidgets.QLineEdit("")
        self.filter_label2 = QtWidgets.QLabel("GroupFilter:")
        self.group_filter_line = QtWidgets.QLineEdit("")

        self.layout().addWidget(self.select_button, ui_row, 0)
        self.layout().addWidget(self.filter_label1, ui_row, 1)
        self.layout().addWidget(self.weight_filter_line, ui_row, 2)
        self.layout().addWidget(self.filter_label2, ui_row, 3)
        self.layout().addWidget(
            self.group_filter_line, ui_row, 4, 1, len(weight_button_value) - 1
        )
        # テーブル配置
        ui_row = 4
        self.layout().addWidget(
            self.tablewidget, ui_row, 0, 2, len(weight_button_value)
        )
        self.set_table(object_cls)

        # ----------Event--------------
        # モードボタン
        for i, button in enumerate(self.mode_button):
            button.clicked.connect(self.clicked_mode_button)
        # ウェイトボタン
        for i, button in enumerate(self.weight_button):
            button.clicked.connect(self.clicked_weight_button)
        # スライダー
        self.slider.valueChanged.connect(self.slider_changed)
        self.slider.sliderPressed.connect(lambda: self.slider_toggle(True))
        self.slider.sliderReleased.connect(lambda: self.slider_toggle(False))
        # フィルター
        self.select_button.clicked.connect(self.select_button_clicked)
        self.group_filter_line.returnPressed.connect(self.table_filter)
        # テーブル
        self.tablewidget.itemClicked.connect(self.item_Clicked)
        # self.tablewidget.itemChanged.connect(lambda: print("item_change"))
        self.tablewidget.itemChanged.connect(self.entered_item)
        # self.tablewidget.currentCellChanged.connect(lambda: print("currentItemChanged"))
        self.tablewidget.itemSelectionChanged.connect(self.item_select_changed)
        # self.tablewidget.itemEntered.connect(lambda: print("itemEntered"))

    def select_button_clicked(self):
        self.select_button_click = True
        self.item_select_changed()

    def item_Clicked(self, item):
        items = self.tablewidget.selectedItems()
        row_set = []
        # if self.focus_mode or self.select_button_click:
        if self.focus_mode:
            for idx in items:
                row_set.append(idx.row())
            self.select_vertex(row_set)

    def slider_toggle(self, mode=False):
        if mode:
            self.slider_press = True
        else:
            self.slider_press = False

    def item_select_changed(self):
        sender = self.sender()
        try:
            text = sender.text()
        except:
            text = None
        items = self.tablewidget.selectedItems()
        item = items[0]
        active_name = self.object_cls.get_vertex_group_index(
            self.tablewidget.horizontalHeaderItem(item.column()).text()
        )
        self.change_active_group(active_name)
        row_set = []
        # if self.focus_mode or self.select_button_click:
        if self.focus_mode or text == "SELECT":
            for idx in items:
                row_set.append(idx.row())
            self.select_vertex(row_set)

    def change_active_group(self, group_index):
        self.object_cls.vertex_groups.active_index = group_index

    def entered_item(self, item):
        # print("entered_item")
        if self.weight_button_clicked:
            return
        if self.select_button_click:
            return
        if self.slider_press:
            return
        if not self.multi_change:
            return
        self.multi_change = False
        for i in self.tablewidget.selectedItems():
            if item.row() == i.row() and item.column() == i.column():
                if item.text() == "---":
                    continue
                value = float(item.text())
                self.change_weight(value=value, mode="REPLACE")

    def mirror_vertex_group(self):
        window = bpy.context.window_manager.windows[0]
        # obj = bpy.context.object
        with bpy.context.temp_override(window=window):
            bpy.ops.object.vertex_group_mirror(
                mirror_weights=True, flip_group_names=True
            )

    def select_vertex_release(self):
        window = bpy.context.window_manager.windows[0]
        with bpy.context.temp_override(window=window):
            if bpy.context.mode == "OBJECT":
                return
            # 現在アクティブなオブジェクトを取得
            obj = bpy.context.active_object
            # 編集モードに切り替え
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action="DESELECT")  # 頂点を全選択
            # ビューポートを更新するために一時的にオブジェクトモードに切り替える
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")

    def select_vertex(self, index=None):
        self.select_vertex_release()

        if index == None:
            return
        window = bpy.context.window_manager.windows[0]
        with bpy.context.temp_override(window=window):
            if bpy.context.mode == "OBJECT":
                return
            # 現在アクティブなオブジェクトを取得
            obj = bpy.context.active_object
            # 編集モードに切り替え
            bpy.ops.object.mode_set(mode="EDIT")
            # BMeshオブジェクトを取得
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            bm.verts.ensure_lookup_table()
            for i in index:
                bm.verts[i].select = True
            bmesh.update_edit_mesh(me)
            # ビューポートを更新するために一時的にオブジェクトモードに切り替える
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.mode_set(mode="EDIT")

    def clicked_mode_button(self):
        logger.info("tb: %s", "".join(traceback.format_stack()))
        print("clicked_mode_button")
        object_cls = self.object_cls
        sender = self.sender()
        text = sender.text()
        self.select_vertex()
        if text == "Mirror":
            self.mirror_vertex_group()
            pass
        for i, idx in enumerate(self.mode_button):
            self.mode_button[i].setText(
                self.mode_button[i].text().replace(":ON", ":OFF")
            )

        self.hilight_mode = False
        self.focus_mode = False
        if text == "Hilight:ON":
            self.hilight_mode = False
            sender.setText("Hilight:OFF")
            self.table_filter()
        elif text == "Hilight:OFF":
            self.hilight_mode = True
            sender.setText("Hilight:ON")
            self.table_filter()
        elif text == "Focus:OFF":
            self.focus_mode = True
            sender.setText("Focus:ON")
        elif text == "Focus:ON":
            self.focus_mode = False
            self.select_button_click = True
            sender.setText("Focus:OFF")
        elif text == "ShowAll:OFF":
            self.show_all_mode = True
            sender.setText("ShowAll:ON")
            # self.set_table(object_cls)
        elif text == "ShowAll:ON":
            self.show_all_mode = False
            sender.setText("ShowAll:OFF")
            # self.set_table(object_cls)

    def select_table_item(self, item):
        print("Clicked!")
        self.item_clicked = True
        self.weight_button_clicked = False

        if not item.text() == "---":
            self.slider.setValue(float(item.text()))
            self.set_slider_text(item.text())
        else:
            self.set_slider_text("---")

    def set_slider_text(self, value):
        self.line2.setText(value)

    def set_table(self, object_cls):
        if self.select_button_click:
            return
        print("set_table")
        """UI設定更新"""
        self.line1.setText(object_cls.name)
        self.tablewidget.setColumnCount(object_cls.colcnt)
        self.tablewidget.setRowCount(object_cls.rowcnt)
        if object_cls.object == None:
            return
        Vgroups_name = object_cls.vertex_groups_name()
        self.tablewidget.setHorizontalHeaderLabels(Vgroups_name)

        """ テーブルの中身作成 """
        count_row = 0
        for column, group in enumerate(object_cls.vertex_groups):
            for row in range(object_cls.rowcnt):
                try:
                    text = str(util.convert_percent(group.weight(row)))
                    item = self.tablewidget.item(row, column)
                    self.tablewidget.setItem(
                        row, column, QtWidgets.QTableWidgetItem(text)
                    )
                except Exception:
                    text = "---"
                    item = self.tablewidget.item(row, column)
                    self.tablewidget.setItem(
                        row, column, QtWidgets.QTableWidgetItem(text)
                    )

        self.table_filter()
        """
        cord_list = ["X", "Y", "Z"]
        Vgroups_name = cord_list + Vgroups_name
        """

    def table_filter(self):
        util.timer_start()
        object_cls = self.object_cls
        # Row_頂点フィルター(選択しているか判断)
        headder_row = []
        if self.hilight_mode:
            # 頂点番号をヘッダーに設定
            for i, idx in enumerate(object_cls.select_vertex):
                if idx:
                    headder_row.append(i)
        else:
            for i in range(object_cls.vertex_count):
                headder_row.append(i)

        # Column_グループフィルター
        filter_name = self.group_filter_line.text()
        filter_group = self.column_filter_name(filter_name)
        self.filter_column(name=filter_group)

        # Row_ウェイトフィルター(頂点)(ウェイトが設定されてない場合)
        del_flag = False
        count_row = 0
        ite = headder_row.copy()
        for row in ite:
            for i, idx in enumerate(object_cls.vertex_groups):
                if not idx.name in filter_group:
                    continue
                try:
                    temp = idx.weight(row)
                    break
                except RuntimeError:
                    pass
            else:
                headder_row.remove(row)
        self.filter_row(headder_row)
        ite = filter_group.copy()
        # Column_ウェイトフィルター(グループ)(ウェイトが設定されてない場合)
        if not self.show_all_mode:
            for i, idx in enumerate(ite):
                for v in headder_row:
                    try:
                        column = object_cls.get_vertex_group_index(idx)
                        temp = object_cls.vertex_groups[column].weight(v)
                        break
                    except RuntimeError:
                        pass
                else:
                    filter_group.remove(idx)
        self.filter_column(name=filter_group)
        util.timer_stop()

    def filter_row(self, index):
        if not index == None:
            if type(index) is int:
                index = list(index)
            for i in range(self.object_cls.vertex_count):
                if i in index:
                    self.tablewidget.setRowHidden(i, False)
                else:
                    self.tablewidget.setRowHidden(i, True)

    def filter_column(self, *, name=None, index=None):
        column_list = self.column_item_list()
        if not name == None:
            if type(name) is str:
                name = list(name)
            for idx in self.object_cls.vertex_groups:
                if idx.name in name:
                    self.tablewidget.setColumnHidden(column_list.index(idx.name), False)
                else:
                    self.tablewidget.setColumnHidden(column_list.index(idx.name), True)
            return
        if not index == None:
            if type(index) is int:
                index = list(index)
            for i, idx in enumerate(column_list):
                if i in index:
                    self.tablewidget.setColumnHidden(i, False)
                else:
                    self.tablewidget.setColumnHidden(i, True)

    def column_filter_name(self, filter_name):
        column_list = self.column_item_list()
        split_name = ","
        filter_name = filter_name.split(split_name)
        res = []
        for idx in column_list:
            for split in filter_name:
                if split.lower() in idx.lower():
                    res.append(idx)
                elif split == "":
                    res.append(idx)
        return res

    def show(self):
        super(Window, self).show()

    def ui_close(self):
        super(Window, self).close()

    def get_table_row(self, row_header):
        for i in range(self.object_cls.vertex_count):
            if row_header == int(self.tablewidget.verticalHeaderItem(i).text()):
                return i
        return None

    def column_select(self):
        self.tablewidget.selectedRanges()
        a = self.tablewidget.selectedRanges()

    def on_update(self, object=None):
        if self.object_cls.name == object.name:
            if self.focus_mode:
                return
            if self.hilight_mode:
                for i, idx in enumerate(self.object_cls.select_vertex):
                    if not idx == object.vertex[i].select:
                        break
                else:
                    return
                self.object_cls = object
                self.table_filter()
        else:
            self.object_cls = object
            if self.select_button_click:
                self.select_button_click = False
                return
            self.set_table(object)

    def change_weight(self, *, value=0, mode=None):
        print("change_weight")
        """
        if self.edit_mode_toggle:
            return
        """
        if mode is None:
            mode = self.weight_mode
        selected_Items = self.tablewidget.selectedItems()
        object_cls = self.object_cls
        idx_dic = {}
        window = bpy.context.window_manager.windows[0]
        EDIT_MESH_MODE = False
        with bpy.context.temp_override(window=window):
            if bpy.context.mode == "EDIT_MESH":
                EDIT_MESH_MODE = True
                bpy.ops.object.mode_set(mode="OBJECT")
            for item in selected_Items:
                # UI
                idx = self.tablewidget.indexFromItem(item)
                group_index = object_cls.get_vertex_group_index(
                    self.tablewidget.horizontalHeaderItem(idx.column()).text()
                )
                # Object_Weight_Table
                Vgroup = object_cls.vertex_group(group_index)
                table_row = int(item.row())
                try:
                    idx_dic[table_row].append(group_index)
                except KeyError:
                    idx_dic[table_row] = []
                    idx_dic[table_row].append(group_index)
                # UIの行を配列化(配列化しないとvertex_group.addメソッドが使えない)
                array = []
                array.append(table_row)
                # 「DELTE」ボタンクリック
                if mode == "DELETE":
                    Vgroup.remove(array)
                    idx_dic[table_row].remove(group_index)
                    weight = -1

                # 加算モード
                if mode == "ADD":
                    Vgroup.add(array, abs(float(value) / 100), mode)
                    weight = util.convert_percent(Vgroup.weight(array[0]))

                try:
                    # 置き換えモード
                    if mode == "REPLACE":
                        Vgroup.add(array, abs(float(value) / 100), mode)
                        weight = util.convert_percent(Vgroup.weight(array[0]))

                    # 減算モード
                    if mode == "SUBTRACT":
                        calc_weight = Vgroup.weight(table_row) + (float(value) / 100)
                        if calc_weight > 0:
                            Vgroup.add(array, abs(float(value) / 100), mode)
                        else:
                            Vgroup.add(array, 0, "REPLACE")
                        weight = util.convert_percent(Vgroup.weight(array[0]))

                except Exception as e:
                    # 頂点グループがない場合
                    tb = sys.exc_info()[2]
                    print(e.with_traceback(tb))
                    weight = -1

                # UI表の値を設定
                self.set_table_item(item.row(), item.column(), weight)
                self.slider.setValue(weight)
            # ノーマライズ
            if self.normalize_mode:
                self.normalize_vertex(idx_dic)
            if EDIT_MESH_MODE:
                bpy.ops.object.mode_set(mode="EDIT")

    def clicked_weight_button(self):
        self.weight_button_clicked = True
        object_cls = self.object_cls
        sender = self.sender()
        selected_Items = self.tablewidget.selectedItems()
        # 「DELTE」ボタンクリック
        if sender.text() == "DELETE":
            self.change_weight(mode="DELETE")
            return
        # AutoNormalize ON/OFF
        if sender.text() == "AutoNormalize:OFF":
            self.normalize_mode = True
            sender.setText("AutoNormalize:ON")
            return
        if sender.text() == "AutoNormalize:ON":
            self.normalize_mode = False
            sender.setText("AutoNormalize:OFF")
            return
        self.change_weight(value=sender.text())

    def column_item_list(self):
        res = []
        for i in range(self.tablewidget.columnCount()):
            res.append(self.tablewidget.horizontalHeaderItem(i).text())
        return res

    def column_item_index(self, name):
        for i in range(self.tablewidget.columnCount()):
            if name == self.tablewidget.horizontalHeaderItem(i).text():
                return i
        else:
            return -1

    def normalize_vertex(self, dic):
        print("normalize_vertex")
        val = 0
        object_cls = self.object_cls
        array = [0]
        for row in dic:
            array[0] = row
            table_row = self.get_table_row(row)

            weight_array = self.vertex_weights(row)
            change_weight_value = self.calc_normalize_vertex(weight_array, dic[row])
            for i, idx in enumerate(object_cls.vertex_groups):
                Vgroup = object_cls.vertex_group(i)
                if not change_weight_value[i] == -1:
                    Vgroup.add(array, change_weight_value[i], "REPLACE")
                    if Vgroup.name in self.column_item_list():
                        self.set_table_item(
                            table_row,
                            self.column_item_index(Vgroup.name),
                            util.convert_percent(change_weight_value[i]),
                        )
                else:
                    if Vgroup.name in self.column_item_list():
                        self.set_table_item(
                            table_row, self.column_item_index(Vgroup.name), -1
                        )

    def calc_normalize_vertex(self, value_array, toggle_array):
        array = value_array.copy()
        max_value = 1
        ZeroFlag = False
        # 変更があるウェイトをスキップするように
        for i in toggle_array:
            max_value -= value_array[i]
            value_array[i] = -2
        calc_array = 0
        calc_sum = 0
        for i in value_array:
            if i > 0:
                calc_sum += i
        try:
            l_convert = max_value / calc_sum
        except ZeroDivisionError:
            div_count = 0
            for i in value_array:
                if i == 0:
                    div_count += 1
            if div_count == 0:
                # 選択したアイテムがすべて0の場合
                div_count = len(toggle_array)
            l_convert = (1 - max_value) / div_count
            ZeroFlag = True
        for i, idx in enumerate(value_array):
            if not ZeroFlag:
                if idx >= 0:
                    array[i] = idx * l_convert
            else:
                if idx == 0:
                    array[i] = l_convert

        return array

    def vertex_weights(self, vertex_index):
        object_cls = self.object_cls
        weight_array = []
        array = [vertex_index]
        for i, idx in enumerate(object_cls.vertex_groups):
            Vgroup = object_cls.vertex_group(i)
            try:
                weight_array.append(Vgroup.weight(array[0]))
            except:
                weight_array.append(-1)
        return weight_array

    def set_table_item(self, row, column, val):
        print("set_table_item")
        if val < 0:
            val = "---"
        item = self.tablewidget.item(row, column)
        item.setText(str(val))

    def itemChanged(self):
        pass

    def slider_changed(self, value):
        print("slider_changed")
        sender = self.sender()
        if not self.item_clicked:
            self.change_weight(value=value, mode="REPLACE")
        self.set_slider_text(str(value))
        self.item_clicked = False

    def keyPressEvent(self, event):
        print("keyPressEvent")
        if event.isAutoRepeat():
            return
        key_Message = "pressed"
        pressed = QtGui.QKeySequence(event.key()).toString(
            QtGui.QKeySequence.NativeText
        )
        self.select_button_click = False
        if pressed == "Control":
            self.CtrKeyAction(key_Message)
        if pressed == "Shift":
            self.ShiftKeyAction(key_Message)
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for i in numbers:
            if pressed == i:
                self.multi_change = True

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

    def set_edit_mode(self, bool, mode=None):
        self.edit_mode_toggle = bool

        """
        オートミラー
        複数頂点選択状態でのスライド速度改善
        ウェイト数値でフィルター
        セル選択から頂点選択
        ノーマライズボタン
        """
