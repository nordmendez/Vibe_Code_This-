import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

class VibeCodeThisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe_Code-This")
        self.setGeometry(100, 100, 1000, 600)

def main():
    app = QApplication(sys.argv)
    window = VibeCodeThisWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
