import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTreeWidget, 
                             QListWidget, QTextEdit, QLineEdit, QSplitter,
                             QColorDialog, QInputDialog, QMessageBox, QMenu,
                             QTreeWidgetItem, QListWidgetItem, QToolTip, QFontComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCharFormat, QColor, QCursor, QGuiApplication, QTextCursor, QFont, QTextListFormat, QPen

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
        self.block_format.setBackground(QColor("#E8E8E8")) # Lighter grey
        
        # Simulate an inline border using overline and underline
        self.block_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        self.block_format.setUnderlineColor(QColor("black"))
        self.block_format.setFontOverline(True)

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
        
        # Re-apply format if still in copy block
        if self.in_copy_block and self.currentCharFormat() != self.block_format:
            self.setCurrentCharFormat(self.block_format)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            fmt = cursor.charFormat()
            bg_color = fmt.background().color()
            
            # Detect by background color since UserProperty doesn't survive HTML serialization
            if bg_color.isValid() and bg_color.name().upper() == "#E8E8E8":
                left_cursor = QTextCursor(cursor)
                while left_cursor.position() > 0:
                    left_cursor.movePosition(QTextCursor.MoveOperation.Left)
                    left_bg = left_cursor.charFormat().background().color()
                    if not left_bg.isValid() or left_bg.name().upper() != "#E8E8E8":
                        left_cursor.movePosition(QTextCursor.MoveOperation.Right)
                        break
                        
                right_cursor = QTextCursor(cursor)
                doc_length = self.document().characterCount()
                while right_cursor.position() < doc_length - 1:
                    right_cursor.movePosition(QTextCursor.MoveOperation.Right)
                    right_bg = right_cursor.charFormat().background().color()
                    if not right_bg.isValid() or right_bg.name().upper() != "#E8E8E8":
                        break
                        
                selection_cursor = QTextCursor(left_cursor)
                selection_cursor.setPosition(right_cursor.position(), QTextCursor.MoveMode.KeepAnchor)
                selected_text = selection_cursor.selectedText()
                if selected_text:
                    QGuiApplication.clipboard().setText(selected_text)
                    QToolTip.showText(QCursor.pos(), "Copied to clip board", self)


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
        self.list_tasks.model().rowsMoved.connect(lambda: self.save_current_folder_tasks(self.tree_folders.currentItem()))
        
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
        
        # Formatting Toolbar
        self.formatting_widget = QWidget()
        self.format_layout = QHBoxLayout(self.formatting_widget)
        self.format_layout.setContentsMargins(0, 0, 0, 0)
        
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.change_font)
        self.format_layout.addWidget(self.font_combo)
        
        self.btn_bold = QPushButton("B")
        self.btn_bold.setCheckable(True)
        self.btn_bold.clicked.connect(self.toggle_bold)
        self.format_layout.addWidget(self.btn_bold)
        
        self.btn_underline = QPushButton("U")
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(self.toggle_underline)
        self.format_layout.addWidget(self.btn_underline)
        
        self.btn_center = QPushButton("Center")
        self.btn_center.clicked.connect(self.align_center)
        self.format_layout.addWidget(self.btn_center)
        
        self.btn_bullet = QPushButton("• List")
        self.btn_bullet.clicked.connect(self.insert_bullet)
        self.format_layout.addWidget(self.btn_bullet)
        
        self.btn_number = QPushButton("1. List")
        self.btn_number.clicked.connect(self.insert_number)
        self.format_layout.addWidget(self.btn_number)
        
        self.text_editor = CustomTextEditor()
        self.text_editor.textChanged.connect(self.save_task_note)
        self.btn_toggle_edit.clicked.connect(self.toggle_edit_mode)
        self.btn_trans.clicked.connect(self.spawn_translucent_window)
        
        self.col3_layout.addLayout(self.col3_header)
        self.col3_layout.addWidget(self.formatting_widget)
        self.col3_layout.addWidget(self.text_editor)
        
        self.formatting_widget.hide()
        
        self.splitter.addWidget(self.col1_widget)
        self.splitter.addWidget(self.col2_widget)
        self.splitter.addWidget(self.col3_widget)
        self.splitter.setSizes([300, 300, 600])
        
        self.main_layout.addWidget(self.splitter)

    def spawn_translucent_window(self):
        self.trans_win = TranslucentWindow(self.text_editor.toHtml())
        self.trans_win.show()

    def save_current_folder_tasks(self, folder):
        if not folder: return
        tasks_data = []
        for i in range(self.list_tasks.count()):
            item = self.list_tasks.item(i)
            tasks_data.append({
                "name": item.text(),
                "note": item.data(Qt.ItemDataRole.UserRole),
                "color": item.foreground().color()
            })
        folder.setData(0, Qt.ItemDataRole.UserRole + 1, tasks_data)

    def add_folder(self):
        name, ok = QInputDialog.getText(self, "New Root Folder", "Folder Name:")
        if ok and name:
            color = QColorDialog.getColor(title="Optional Folder Color")
            parent = self.tree_folders.invisibleRootItem()
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
        a_add_sub = menu.addAction("Add New Folder")
        a_rename = menu.addAction("Rename")
        a_dup = menu.addAction("Duplicate")
        a_del = menu.addAction("Delete")
        a_color = menu.addAction("Change Color")
        
        action = menu.exec(self.tree_folders.mapToGlobal(pos))
        if action == a_add_sub:
            name, ok = QInputDialog.getText(self, "New Subfolder", "Subfolder Name:")
            if ok and name:
                new_item = QTreeWidgetItem(item)
                new_item.setText(0, name)
                color = item.data(0, Qt.ItemDataRole.UserRole)
                if color and color.isValid():
                    self.apply_color_to_folder(new_item, color)
                item.setExpanded(True)
        elif action == a_rename:
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
        if previous:
            self.save_current_folder_tasks(previous)
            
        self.list_tasks.clear()
        self.text_editor.clear()
        self.lbl_selected_folder.setText("Select a folder")
        
        if current:
            self.lbl_selected_folder.setText(current.text(0))
            color = current.data(0, Qt.ItemDataRole.UserRole)
            
            tasks_data = current.data(0, Qt.ItemDataRole.UserRole + 1) or []
            for tdata in tasks_data:
                item = QListWidgetItem(tdata["name"])
                item.setData(Qt.ItemDataRole.UserRole, tdata["note"])
                if tdata.get("color") and tdata["color"].isValid():
                    item.setForeground(tdata["color"])
                self.list_tasks.addItem(item)
                
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
            self.save_current_folder_tasks(folder)

    def on_task_selected(self, current, previous):
        if current:
            note_content = current.data(Qt.ItemDataRole.UserRole) or ""
            self.text_editor.blockSignals(True)
            self.text_editor.setHtml(note_content)
            self.text_editor.blockSignals(False)
            if not note_content.strip():
                self.text_editor.setReadOnly(False)
                self.formatting_widget.show()
            else:
                self.text_editor.setReadOnly(True)
                self.formatting_widget.hide()
        else:
            self.text_editor.clear()
            self.text_editor.setReadOnly(True)
            self.formatting_widget.hide()

    def change_font(self, font):
        self.text_editor.setCurrentFont(font)

    def toggle_bold(self):
        self.text_editor.setFontWeight(700 if self.btn_bold.isChecked() else 400)

    def toggle_underline(self):
        self.text_editor.setFontUnderline(self.btn_underline.isChecked())

    def align_center(self):
        self.text_editor.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def insert_bullet(self):
        cursor = self.text_editor.textCursor()
        cursor.createList(QTextListFormat.Style.ListDisc)

    def insert_number(self):
        cursor = self.text_editor.textCursor()
        cursor.createList(QTextListFormat.Style.ListDecimal)

    def toggle_edit_mode(self):
        new_state = not self.text_editor.isReadOnly()
        self.text_editor.setReadOnly(new_state)
        self.formatting_widget.setVisible(not new_state)

    def save_task_note(self):
        item = self.list_tasks.currentItem()
        if item:
            item.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())
            self.save_current_folder_tasks(self.tree_folders.currentItem())

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
