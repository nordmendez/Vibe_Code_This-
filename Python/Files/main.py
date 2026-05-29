import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTreeWidget, 
                             QListWidget, QTextEdit, QLineEdit, QSplitter,
                             QColorDialog, QInputDialog, QMessageBox, QMenu,
                             QTreeWidgetItem, QListWidgetItem, QFontComboBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRectF, QPointF
from PyQt6.QtGui import (QTextCharFormat, QColor, QCursor, QGuiApplication, 
                         QTextCursor, QFont, QTextListFormat, QPen, 
                         QTextTableFormat, QBrush, QTextFrameFormat, QPainter)

class ToastWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            color: #FFFFFF;
            padding: 6px 12px;
            font-size: 14px;
            font-weight: bold;
        """)
        self.setText("Copied to clipboard!")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hide()
        
    def show_toast(self, pos):
        self.adjustSize()
        self.move(pos.x() - self.width() // 2, pos.y() - self.height() // 2)
        self.show()
        QTimer.singleShot(1000, self.hide)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor("#000000")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 4.0, 4.0)
        painter.end()
        super().paintEvent(event)

class CustomTextEditor(QTextEdit):
    # Class level constant for the lightened copy box background
    COPY_BG = "#FAFAFA"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setPlaceholderText("Select text and click '🔲 Copy' to make it a copy block")
        
        self.default_format = QTextCharFormat()
        
        self.block_format = QTextCharFormat()
        self.block_format.setBackground(QColor(self.COPY_BG))
        self.block_format.setFontFamily("Courier")


    def create_copy_block(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(self.block_format)
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.setCurrentCharFormat(self.default_format)

    def keyPressEvent(self, event):
        # Reset typing format if it has inherited the COPY_BG, ensuring new characters are default format
        if event.text():
            fmt = self.currentCharFormat()
            brush = fmt.background()
            if brush.style() != Qt.BrushStyle.NoBrush:
                bg_color = brush.color()
                if bg_color.isValid() and bg_color.name().upper() == self.COPY_BG:
                    self.setCurrentCharFormat(self.default_format)
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            block = cursor.block()
            block_pos = block.position()
            click_rel_pos = cursor.position() - block_pos
            
            formats = block.textFormats()
            for fmt_range in formats:
                start = fmt_range.start
                length = fmt_range.length
                fmt = fmt_range.format
                
                brush = fmt.background()
                if brush.style() != Qt.BrushStyle.NoBrush:
                    bg_color = brush.color()
                    if bg_color.isValid() and bg_color.name().upper() == self.COPY_BG:
                        if start <= click_rel_pos <= start + length:
                            selection_cursor = QTextCursor(self.document())
                            selection_cursor.setPosition(block_pos + start)
                            selection_cursor.setPosition(block_pos + start + length, QTextCursor.MoveMode.KeepAnchor)
                            selected_text = selection_cursor.selectedText()
                            
                            if selected_text:
                                QGuiApplication.clipboard().setText(selected_text)
                                if not hasattr(self, 'toast'):
                                    self.toast = ToastWidget()
                                self.toast.show_toast(event.globalPosition().toPoint())
                            break

    def paintEvent(self, event):
        # Draw the standard text and background highlight first
        super().paintEvent(event)
        
        # Use QPainter to draw a clean, thin border around the copy block(s)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Thin neutral grey/black border
        pen = QPen(QColor("#888888"), 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        
        doc = self.document()
        doc_layout = doc.documentLayout()
        
        # 1. Get exact scroll offsets (No margins!)
        x_offset = self.horizontalScrollBar().value()
        y_offset = self.verticalScrollBar().value()
        
        block = doc.begin()
        while block.isValid():
            block_rect = doc_layout.blockBoundingRect(block)
            block_pos = block_rect.topLeft()
            
            formats = block.textFormats()
            for fmt_range in formats:
                start = fmt_range.start
                length = fmt_range.length
                fmt = fmt_range.format
                
                bg_color = fmt.background().color()
                if bg_color.isValid() and bg_color.name().upper() == self.COPY_BG:
                    run_start = start
                    run_end = start + length
                    block_layout = block.layout()
                    
                    for line_idx in range(block_layout.lineCount()):
                        line = block_layout.lineAt(line_idx)
                        line_start = line.textStart()
                        line_end = line_start + line.textLength()
                        
                        intersect_start = max(run_start, line_start)
                        intersect_end = min(run_end, line_end)
                        
                        if intersect_start < intersect_end:
                            # 2. cursorToX returns a tuple, grab the float at index 0. 
                            # This X is relative to the block layout.
                            x1 = line.cursorToX(intersect_start)[0]
                            x2 = line.cursorToX(intersect_end)[0]
                            
                            # 3. The Flawless Math: Block Pos + Relative Pos - Scrollbar
                            vx1 = block_pos.x() + x1 - x_offset
                            vx2 = block_pos.x() + x2 - x_offset
                            vy = block_pos.y() + line.y() - y_offset
                            vh = line.height()
                            
                            # 4. Apply the breathing room padding and draw
                            pad_x = 2
                            pad_y = 1
                            rect = QRectF(vx1 - pad_x, vy - pad_y, (vx2 - vx1) + (pad_x * 2), vh + (pad_y * 2))
                            
                            painter.drawRoundedRect(rect, 3, 3)
            
            block = block.next()

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
        
        # Re-use CustomTextEditor so copy block works here too
        self.text_display = CustomTextEditor()
        self.text_display.setReadOnly(True)
        self.text_display.setHtml(text_content)
        layout.addWidget(self.text_display)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if hasattr(self, '_drag_position'):
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()


class VibeCodeThisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe_Code-This")
        self.setGeometry(100, 100, 1200, 700)
        self.unsaved_changes = False
        self.init_ui()
        self.load_workspace()

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
        
        self.btn_import.clicked.connect(self.btn_import_clicked)
        self.btn_save_as.clicked.connect(self.btn_save_as_clicked)
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
        self.tree_folders.model().rowsMoved.connect(self.mark_unsaved)
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
        
        self.btn_copy_block = QPushButton("🔲 Copy")
        self.btn_copy_block.clicked.connect(self.format_as_copy_block)
        self.format_layout.addWidget(self.btn_copy_block)
        
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

    def mark_unsaved(self):
        self.unsaved_changes = True

    def btn_import_clicked(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Workspace", "", "JSON Files (*.json)")
        if path:
            self.load_workspace(path)

    def btn_save_as_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Workspace", "workspace.json", "JSON Files (*.json)")
        if path:
            self.save_workspace(path)

    def spawn_translucent_window(self):
        self.trans_win = TranslucentWindow(self.text_editor.toHtml())
        self.trans_win.show()

    def serialize_folder(self, item):
        color = item.data(0, Qt.ItemDataRole.UserRole)
        tasks = item.data(0, Qt.ItemDataRole.UserRole + 1) or []
        folder_data = {
            "name": item.text(0),
            "color": color.name() if color and color.isValid() else None,
            "tasks": tasks,
            "subfolders": []
        }
        for i in range(item.childCount()):
            folder_data["subfolders"].append(self.serialize_folder(item.child(i)))
        return folder_data

    def save_workspace(self, filepath="workspace.json"):
        # Explicitly save the current active text editor note to the current task item
        # so any formatting changes (which don't trigger textChanged) are perfectly preserved!
        item = self.list_tasks.currentItem()
        if item:
            item.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())
            
        if self.tree_folders.currentItem():
            self.save_current_folder_tasks(self.tree_folders.currentItem())
            
        data = {"folders": []}
        root = self.tree_folders.invisibleRootItem()
        for i in range(root.childCount()):
            data["folders"].append(self.serialize_folder(root.child(i)))
            
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        self.unsaved_changes = False

    def load_workspace(self, filepath="workspace.json"):
        if not os.path.exists(filepath): return
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except Exception:
                return
        
        self.tree_folders.clear()
        self.list_tasks.clear()
        self.text_editor.clear()
        
        for f_data in data.get("folders", []):
            self.deserialize_folder(f_data, self.tree_folders.invisibleRootItem())
            
        self.unsaved_changes = False

    def deserialize_folder(self, data, parent_item):
        item = QTreeWidgetItem(parent_item)
        item.setText(0, data.get("name", "Untitled"))
        color_hex = data.get("color")
        if color_hex:
            color = QColor(color_hex)
            item.setData(0, Qt.ItemDataRole.UserRole, color)
            item.setForeground(0, color)
        
        item.setData(0, Qt.ItemDataRole.UserRole + 1, data.get("tasks", []))
        
        for sub_data in data.get("subfolders", []):
            self.deserialize_folder(sub_data, item)

    def save_current_folder_tasks(self, folder):
        if not folder: return
        tasks_data = []
        for i in range(self.list_tasks.count()):
            item = self.list_tasks.item(i)
            c = item.foreground().color()
            tasks_data.append({
                "name": item.text(),
                "note": item.data(Qt.ItemDataRole.UserRole),
                "color": c.name() if c.isValid() else None
            })
        folder.setData(0, Qt.ItemDataRole.UserRole + 1, tasks_data)
        self.mark_unsaved()

    def add_folder(self):
        name, ok = QInputDialog.getText(self, "New Root Folder", "Folder Name:")
        if ok and name:
            color = QColorDialog.getColor(title="Optional Folder Color")
            parent = self.tree_folders.invisibleRootItem()
            item = QTreeWidgetItem(parent)
            item.setText(0, name)
            if color.isValid():
                self.apply_color_to_folder(item, color)
            self.mark_unsaved()

    def apply_color_to_folder(self, item, color):
        item.setData(0, Qt.ItemDataRole.UserRole, color)
        item.setForeground(0, color)
        for i in range(item.childCount()):
            self.apply_color_to_folder(item.child(i), color)
        
        if item == self.tree_folders.currentItem():
            self.update_cascading_color(color)
        self.mark_unsaved()

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
                self.mark_unsaved()
        elif action == a_rename:
            name, ok = QInputDialog.getText(self, "Rename", "New Name:", text=item.text(0))
            if ok and name: 
                item.setText(0, name)
                self.mark_unsaved()
        elif action == a_dup:
            parent = item.parent() or self.tree_folders.invisibleRootItem()
            new_item = QTreeWidgetItem(parent)
            new_item.setText(0, item.text(0) + " (copy)")
            color = item.data(0, Qt.ItemDataRole.UserRole)
            if color: self.apply_color_to_folder(new_item, color)
            self.mark_unsaved()
        elif action == a_del:
            if QMessageBox.question(self, "Confirm", "Delete folder?") == QMessageBox.StandardButton.Yes:
                parent = item.parent() or self.tree_folders.invisibleRootItem()
                parent.removeChild(item)
                self.mark_unsaved()
        elif action == a_color:
            color = QColorDialog.getColor()
            if color.isValid():
                self.apply_color_to_folder(item, color)

    def on_folder_selected(self, current, previous):
        if previous:
            # Explicitly save the current active text editor note to the current task item first
            item = self.list_tasks.currentItem()
            if item:
                item.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())
            self.save_current_folder_tasks(previous)
            
        self.list_tasks.blockSignals(True)
        self.list_tasks.clear()
        self.list_tasks.blockSignals(False)
        
        self.text_editor.clear()
        self.text_editor.setReadOnly(True)
        self.formatting_widget.hide()
        self.lbl_selected_folder.setText("Select a folder")
        
        if current:
            self.lbl_selected_folder.setText(current.text(0))
            color = current.data(0, Qt.ItemDataRole.UserRole)
            
            tasks_data = current.data(0, Qt.ItemDataRole.UserRole + 1) or []
            self.list_tasks.blockSignals(True)
            for tdata in tasks_data:
                item = QListWidgetItem(tdata["name"])
                item.setData(Qt.ItemDataRole.UserRole, tdata["note"])
                if tdata.get("color"):
                    item.setForeground(QColor(tdata["color"]))
                self.list_tasks.addItem(item)
            self.list_tasks.blockSignals(False)
                
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
        if previous:
            # Explicitly save the previous task's note before loading the new one
            previous.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())
            self.save_current_folder_tasks(self.tree_folders.currentItem())
            
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
        self.mark_unsaved()

    def toggle_bold(self):
        self.text_editor.setFontWeight(700 if self.btn_bold.isChecked() else 400)
        self.mark_unsaved()

    def toggle_underline(self):
        self.text_editor.setFontUnderline(self.btn_underline.isChecked())
        self.mark_unsaved()

    def align_center(self):
        self.text_editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mark_unsaved()

    def insert_bullet(self):
        cursor = self.text_editor.textCursor()
        cursor.createList(QTextListFormat.Style.ListDisc)
        self.mark_unsaved()

    def insert_number(self):
        cursor = self.text_editor.textCursor()
        cursor.createList(QTextListFormat.Style.ListDecimal)
        self.mark_unsaved()

    def format_as_copy_block(self):
        self.text_editor.create_copy_block()
        self.mark_unsaved()

    def toggle_edit_mode(self):
        new_state = not self.text_editor.isReadOnly()
        self.text_editor.setReadOnly(new_state)
        self.formatting_widget.setVisible(not new_state)

    def save_task_note(self):
        item = self.list_tasks.currentItem()
        if item:
            item.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())
            self.save_current_folder_tasks(self.tree_folders.currentItem())

    def closeEvent(self, event):
        if self.unsaved_changes:
            reply = QMessageBox.question(self, "Unsaved Changes", 
                                         "You have unsaved changes. Save before closing?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_workspace()
                event.accept()
            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            self.save_workspace() # silent save to default just in case
            event.accept()

    def custom_close(self):
        self.close()

def main():
    app = QApplication(sys.argv)
    window = VibeCodeThisWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
