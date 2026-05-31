import sys
from PyQt6.QtWidgets import QApplication, QWidget
from qfluentwidgets import MessageBoxBase
from src.main import FolderColorDialog

app = QApplication(sys.argv)
parent_win = QWidget()
parent_win.resize(800, 600)
parent_win.show()
dialog = FolderColorDialog(parent_win)
# Automatically click the first color after a short delay
from PyQt6.QtCore import QTimer

def click_color():
    # Find the first QPushButton in the dialog and click it
    from PyQt6.QtWidgets import QPushButton
    btns = dialog.findChildren(QPushButton)
    for btn in btns:
        if btn.text() == "": # Color buttons have no text
            btn.click()
            break

QTimer.singleShot(1000, click_color)
res = dialog.exec()
print(f"Dialog result: {res}")
print(f"Selected color: {dialog.getColor()}")
sys.exit(0)
