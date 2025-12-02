from aqt import mw
from aqt.qt import *
from aqt.utils import qconnect
from .ui import EudicSyncDialog

def show_dialog():
    mw.eudic_dialog = EudicSyncDialog(mw)
    mw.eudic_dialog.show()

# 添加菜单项
action = QAction("EudicSync", mw)
qconnect(action.triggered, show_dialog)
mw.form.menuTools.addAction(action)