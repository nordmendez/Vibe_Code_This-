import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.main import VibeCodeThisWindow

app = QApplication(sys.argv)
win = VibeCodeThisWindow()
win.show()

def test_color_change():
    item = win.tree_folders.topLevelItem(0)
    print("Old color:", item.data(0, 32))
    # Open dialog and click a color
    win.tree_folders.setCurrentItem(item)
    # Simulate action
    from src.main import FolderColorDialog
    from PyQt6.QtGui import QColor
    
    dialog = FolderColorDialog(win)
    
    def click_color():
        from PyQt6.QtWidgets import QPushButton
        btns = dialog.findChildren(QPushButton)
        for btn in btns:
            if btn.text() == "":
                btn.click()
                break

    QTimer.singleShot(500, click_color)
    if dialog.exec():
        color = dialog.getColor()
        if color and color.isValid():
            win.apply_color_to_folder(item, color)
            print("New color applied:", color.name())
    else:
        print("Dialog exec returned false!")
    
    QTimer.singleShot(500, app.quit)

QTimer.singleShot(1000, test_color_change)
app.exec()
