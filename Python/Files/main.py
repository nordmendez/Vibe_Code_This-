import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTreeWidget, 
                             QListWidget, QTextEdit, QLineEdit, QSplitter)
from PyQt6.QtCore import Qt

class VibeCodeThisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe_Code-This")
        self.setGeometry(100, 100, 1200, 700)
        self.init_ui()

    def init_ui(self):
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # --- Top Row Controls ---
        self.top_row_layout = QHBoxLayout()
        self.btn_import = QPushButton("Import")
        self.btn_save_as = QPushButton("Save As")
        self.lbl_selected_folder = QLabel("Select a folder")
        self.lbl_selected_folder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.custom_close)
        
        self.top_row_layout.addWidget(self.btn_import)
        self.top_row_layout.addWidget(self.btn_save_as)
        self.top_row_layout.addWidget(self.lbl_selected_folder, stretch=1)
        self.top_row_layout.addWidget(self.btn_close)
        
        self.main_layout.addLayout(self.top_row_layout)
        
        # --- Three-Column Interface ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Column 1: Folder Tree
        self.col1_widget = QWidget()
        self.col1_layout = QVBoxLayout(self.col1_widget)
        
        self.col1_header = QHBoxLayout()
        self.lbl_col1 = QLabel("Folders")
        self.btn_add_folder = QPushButton("+")
        self.col1_header.addWidget(self.lbl_col1)
        self.col1_header.addStretch()
        self.col1_header.addWidget(self.btn_add_folder)
        
        self.tree_folders = QTreeWidget()
        self.tree_folders.setHeaderHidden(True)
        self.tree_folders.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search folders...")
        
        self.col1_layout.addLayout(self.col1_header)
        self.col1_layout.addWidget(self.tree_folders)
        self.col1_layout.addWidget(self.search_box)
        
        # Column 2: Task List
        self.col2_widget = QWidget()
        self.col2_layout = QVBoxLayout(self.col2_widget)
        
        self.col2_header = QHBoxLayout()
        self.lbl_col2 = QLabel("Tasks")
        self.btn_add_task = QPushButton("+")
        self.col2_header.addWidget(self.lbl_col2)
        self.col2_header.addStretch()
        self.col2_header.addWidget(self.btn_add_task)
        
        self.list_tasks = QListWidget()
        self.list_tasks.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        
        self.col2_layout.addLayout(self.col2_header)
        self.col2_layout.addWidget(self.list_tasks)
        
        # Column 3: Notes & Code Area
        self.col3_widget = QWidget()
        self.col3_layout = QVBoxLayout(self.col3_widget)
        
        self.col3_header = QHBoxLayout()
        self.btn_toggle_edit = QPushButton("✏️")
        self.btn_attach_file = QPushButton("Attach File")
        self.btn_open_file = QPushButton("Open File")
        self.btn_trans = QPushButton("Trans")
        
        self.col3_header.addWidget(self.btn_toggle_edit)
        self.col3_header.addWidget(self.btn_attach_file)
        self.col3_header.addWidget(self.btn_open_file)
        self.col3_header.addStretch()
        self.col3_header.addWidget(self.btn_trans)
        
        self.text_editor = QTextEdit()
        
        self.col3_layout.addLayout(self.col3_header)
        self.col3_layout.addWidget(self.text_editor)
        
        # Add columns to splitter
        self.splitter.addWidget(self.col1_widget)
        self.splitter.addWidget(self.col2_widget)
        self.splitter.addWidget(self.col3_widget)
        
        self.splitter.setSizes([300, 300, 600])
        
        self.main_layout.addWidget(self.splitter)

    def custom_close(self):
        # TODO: Save state to default JSON
        self.close()

def main():
    app = QApplication(sys.argv)
    window = VibeCodeThisWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
