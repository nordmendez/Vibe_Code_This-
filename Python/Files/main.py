import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTreeWidget, 
                             QListWidget, QTextEdit, QLineEdit, QSplitter,
                             QColorDialog, QInputDialog, QMessageBox, QMenu,
                             QTreeWidgetItem, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QColor, QCursor, QGuiApplication

class TranslucentWindow(QWidget):
    def __init__(self, text_content):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowOpacity(0.8)
        self.resize(300, 200)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with close button
        header = QHBoxLayout()
        header.addStretch()
        btn_close = QPushButton("×")
        btn_close.setFixedSize(20, 20)
        btn_close.clicked.connect(self.close)
        header.addWidget(btn_close)
        layout.addLayout(header)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setHtml(text_content)
        layout.addWidget(self.text_display)

class CustomTextEditor(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("Press tab for copy cblock")
        self.in_copy_block = False
        
        self.default_format = QTextCharFormat()
        
        self.block_format = QTextCharFormat()
        self.block_format.setBackground(QColor("lightgray"))
        # Using a custom property to identify the block
        self.block_format.setProperty(QTextCharFormat.Property.UserProperty, True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            self.in_copy_block = True
            self.setCurrentCharFormat(self.block_format)
            return  # Intercept Tab
        
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return):
            if self.in_copy_block:
                self.in_copy_block = False
                self.setCurrentCharFormat(self.default_format)
        
        super().keyPressEvent(event)
        
        # Re-apply format if still in copy block (since some actions might reset it)
        if self.in_copy_block and self.currentCharFormat() != self.block_format:
            self.setCurrentCharFormat(self.block_format)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            fmt = cursor.charFormat()
            if fmt.property(QTextCharFormat.Property.UserProperty) == True:
                # Find the full block
                cursor.select(cursor.SelectionType.WordUnderCursor)
                selected_text = cursor.selectedText()
                if selected_text:
                    QGuiApplication.clipboard().setText(selected_text)
                    print("Copied to clipboard:", selected_text)

class VibeCodeThisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe_Code-This")
        self.setGeometry(100, 100, 1200, 700)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
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
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Column 1
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
        self.tree_folders.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_folders.customContextMenuRequested.connect(self.show_folder_context_menu)
        self.tree_folders.currentItemChanged.connect(self.on_folder_selected)
        self.btn_add_folder.clicked.connect(self.add_folder)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search folders...")
        
        self.col1_layout.addLayout(self.col1_header)
        self.col1_layout.addWidget(self.tree_folders)
        self.col1_layout.addWidget(self.search_box)
        
        # Column 2
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
        self.btn_add_task.clicked.connect(self.add_task)
        self.list_tasks.currentItemChanged.connect(self.on_task_selected)
        
        self.col2_layout.addLayout(self.col2_header)
        self.col2_layout.addWidget(self.list_tasks)
        
        # Column 3
        self.col3_widget = QWidget()
        self.col3_widget.setObjectName("Col3Widget")
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
        
        self.text_editor = CustomTextEditor()
        self.text_editor.textChanged.connect(self.save_task_note)
        self.btn_toggle_edit.clicked.connect(self.toggle_edit_mode)
        self.btn_trans.clicked.connect(self.spawn_translucent_window)
        
        self.col3_layout.addLayout(self.col3_header)
        self.col3_layout.addWidget(self.text_editor)
        
        self.splitter.addWidget(self.col1_widget)
        self.splitter.addWidget(self.col2_widget)
        self.splitter.addWidget(self.col3_widget)
        self.splitter.setSizes([300, 300, 600])
        
        self.main_layout.addWidget(self.splitter)

    def spawn_translucent_window(self):
        self.trans_win = TranslucentWindow(self.text_editor.toHtml())
        self.trans_win.show()

    def add_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder Name:")
        if ok and name:
            color = QColorDialog.getColor(title="Optional Folder Color")
            parent = self.tree_folders.currentItem() or self.tree_folders.invisibleRootItem()
            item = QTreeWidgetItem(parent)
            item.setText(0, name)
            if color.isValid():
                self.apply_color_to_folder(item, color)

    def apply_color_to_folder(self, item, color):
        item.setData(0, Qt.ItemDataRole.UserRole, color)
        item.setForeground(0, color)
        for i in range(item.childCount()):
            self.apply_color_to_folder(item.child(i), color)
        
        if item == self.tree_folders.currentItem():
            self.update_cascading_color(color)

    def update_cascading_color(self, color):
        color_name = color.name() if color and color.isValid() else "transparent"
        for i in range(self.list_tasks.count()):
            self.list_tasks.item(i).setForeground(color if color and color.isValid() else Qt.GlobalColor.black)
        
        border_style = f"2px solid {color_name}" if color_name != "transparent" else "none"
        self.col3_widget.setStyleSheet(f"#Col3Widget {{ border: {border_style}; }}")

    def show_folder_context_menu(self, pos):
        item = self.tree_folders.itemAt(pos)
        if not item: return
        menu = QMenu()
        a_rename = menu.addAction("Rename")
        a_dup = menu.addAction("Duplicate")
        a_del = menu.addAction("Delete")
        a_color = menu.addAction("Change Color")
        
        action = menu.exec(self.tree_folders.mapToGlobal(pos))
        if action == a_rename:
            name, ok = QInputDialog.getText(self, "Rename", "New Name:", text=item.text(0))
            if ok and name: item.setText(0, name)
        elif action == a_dup:
            parent = item.parent() or self.tree_folders.invisibleRootItem()
            new_item = QTreeWidgetItem(parent)
            new_item.setText(0, item.text(0) + " (copy)")
            color = item.data(0, Qt.ItemDataRole.UserRole)
            if color: self.apply_color_to_folder(new_item, color)
        elif action == a_del:
            if QMessageBox.question(self, "Confirm", "Delete folder?") == QMessageBox.StandardButton.Yes:
                parent = item.parent() or self.tree_folders.invisibleRootItem()
                parent.removeChild(item)
        elif action == a_color:
            color = QColorDialog.getColor()
            if color.isValid():
                self.apply_color_to_folder(item, color)

    def on_folder_selected(self, current, previous):
        if current:
            self.lbl_selected_folder.setText(current.text(0))
            color = current.data(0, Qt.ItemDataRole.UserRole)
            self.update_cascading_color(color)

    def add_task(self):
        folder = self.tree_folders.currentItem()
        if not folder:
            QMessageBox.warning(self, "No Folder", "Select a folder first.")
            return
        name, ok = QInputDialog.getText(self, "New Task", "Task Title:")
        if ok and name:
            item = QListWidgetItem(name)
            color = folder.data(0, Qt.ItemDataRole.UserRole)
            if color and color.isValid(): item.setForeground(color)
            self.list_tasks.addItem(item)

    def on_task_selected(self, current, previous):
        if current:
            note_content = current.data(Qt.ItemDataRole.UserRole) or ""
            self.text_editor.blockSignals(True)
            self.text_editor.setHtml(note_content)
            self.text_editor.blockSignals(False)
            if not note_content.strip():
                self.text_editor.setReadOnly(False)
            else:
                self.text_editor.setReadOnly(True)
        else:
            self.text_editor.clear()
            self.text_editor.setReadOnly(True)

    def toggle_edit_mode(self):
        self.text_editor.setReadOnly(not self.text_editor.isReadOnly())

    def save_task_note(self):
        item = self.list_tasks.currentItem()
        if item:
            item.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())

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
