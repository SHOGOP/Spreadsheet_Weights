from pip._internal import main as _main
import importlib
import bpy

bl_info = {
    "name": "Spreadsheet_Weights",
    "author": "将伍P",
    "version": (1, 0),
    "blender": (3, 3, 0),
    "location": "3Dビューポート > Sidebar > Spreadsheet_Weights",
    "description": "スプレッドシート形式でウェイトを設定する",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object",
}


if "bpy" in locals():
    import imp

    imp.reload(main)
    imp.reload(Object_Weight_Table)
    imp.reload(util)
else:
    from . import main
    from . import Object_Weight_Table
    from . import util


def _import(name, module, ver=None):
    try:
        globals()[name] = importlib.import_module(module)
    except ImportError:
        try:
            if ver is None:
                _main(["install", module])
            else:
                _main(["install", "{}=={}".format(module, ver)])
            globals()[name] = importlib.import_module(module)
        except:
            print("can't import: {}".format(module))


# メニューを構築する関数
def menu_fn(self, context):
    self.layout.separator()
    self.layout.operator(main.SpreadSheet_OT_Weights.bl_idname)


# Blenderに登録するクラス
classes = [
    main.SpreadSheet_OT_Weights,
    main.SpreadSheet_PT_Weights,
]


# アドオン有効化時の処理
def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.VIEW3D_MT_object.append(menu_fn)
    print("Spreadsheet_Weights　regist")


# アドオン無効化時の処理
def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_fn)
    for c in classes:
        bpy.utils.unregister_class(c)
    print("Spreadsheet_Weights　unregist")


# メイン処理
if __name__ == "__main__":
    _import("Pyside", "Pyside6", "6.6.1")
    register()
