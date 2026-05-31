import sys
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap
from qfluentwidgets import FluentIcon

app = QApplication(sys.argv)

icon = FluentIcon.FOLDER.icon()
pixmap = icon.pixmap(64, 64)

# Colorize
painter = QPainter(pixmap)
painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
painter.fillRect(pixmap.rect(), QColor("#FF158A"))
painter.end()

label = QLabel()
label.setPixmap(pixmap)
label.show()

# Print if pixmap is null
print("Pixmap isNull:", pixmap.isNull())

QTimer = __import__('PyQt6.QtCore').QtCore.QTimer
QTimer.singleShot(1000, app.quit)
app.exec()
