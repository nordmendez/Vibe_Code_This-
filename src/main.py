import sys
import shutil
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QTreeWidget, QListWidget,
                             QColorDialog, QInputDialog, QMessageBox, QMenu, QPushButton,
                             QTreeWidgetItem, QListWidgetItem, QFontComboBox, QFileDialog, QGridLayout, QTextBrowser)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRectF, QPointF, QSize
from PyQt6.QtGui import (QTextCharFormat, QColor, QCursor, QGuiApplication, 
                         QTextCursor, QFont, QTextListFormat, QPen, 
                         QTextTableFormat, QBrush, QTextFrameFormat, QPainter,
                         QIcon, QPixmap, QPainterPath, QLinearGradient)
from qfluentwidgets import (MessageBoxBase, PushButton, SubtitleLabel, BodyLabel, CaptionLabel,
                            TreeWidget, ListWidget, TextEdit, LineEdit, setTheme, Theme, setThemeColor, SearchLineEdit, TransparentPushButton, InfoBar, InfoBarPosition)
from qframelesswindow import FramelessWindow

def get_workspace_path(filename="workspace.json"):
    # Determine the bundled template path
    if getattr(sys, 'frozen', False):
        bundled_path = os.path.join(sys._MEIPASS, filename)
    else:
        bundled_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)

    # For production macOS, use ~/Library/Application Support/VibeCodeThis
    if sys.platform == 'darwin':
        user_data_dir = os.path.expanduser("~/Library/Application Support/VibeCodeThis")
    else:
        # Fallback to local dir for other OS or dev
        user_data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    os.makedirs(user_data_dir, exist_ok=True)
    user_file_path = os.path.join(user_data_dir, filename)
    
    # If the user doesn't have a workspace yet, copy the introductory template!
    if not os.path.exists(user_file_path) and os.path.exists(bundled_path) and user_file_path != bundled_path:
        shutil.copy2(bundled_path, user_file_path)
        
    return user_file_path


class FolderColorDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('Choose Folder Color')
        self.viewLayout.addWidget(self.titleLabel)

        self.color_grid = QGridLayout()
        self.viewLayout.addLayout(self.color_grid)

        # Monday.com style palette
        self.colors = [
            "#FF158A", "#FF5AC4", "#BB3354", "#7F5347", "#FF642E", 
            "#FFCB00", "#9CD326", "#037F4C", "#00C875", "#9AADBD", 
            "#0086C0", "#579BFC", "#66CCFF", "#A25DDC", "#784BD1", 
            "#808080", "#333333", "#E2445C", "#FDAB3D", "#000000"
        ]
        
        self.selected_color = None
        
        row = 0
        col = 0
        for color in self.colors:
            btn = TransparentPushButton()
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 16px;
                }}
                QPushButton:hover {{
                    border: 2px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color: self.set_color(c))
            self.color_grid.addWidget(btn, row, col)
            col += 1
            if col > 4:
                col = 0
                row += 1

        self.hex_input = LineEdit()
        self.hex_input.setPlaceholderText("Or enter Hex (#FFFFFF)")
        self.hex_input.textChanged.connect(self.on_hex_changed)
        self.viewLayout.addWidget(self.hex_input)
        
        self.widget.setMinimumWidth(250)

    def set_color(self, color):
        self.selected_color = QColor(color)
        self.accept()

    def on_hex_changed(self, text):
        if len(text) == 7 and text.startswith('#'):
            self.selected_color = QColor(text)
            
    def getColor(self):
        return self.selected_color

class ToastWidget(BodyLabel):
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

class CustomTextEditor(TextEdit):
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
        
        # Disable copy functionality in edit mode
        if not self.isReadOnly():
            return
            
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
                        # Only copy if the exact click position is visually inside the drawn bounding box
                        clicked_on_box = False
                        block_layout = block.layout()
                        for line_idx in range(block_layout.lineCount()):
                            line = block_layout.lineAt(line_idx)
                            line_start = line.textStart()
                            line_end = line_start + line.textLength()
                            
                            intersect_start = max(start, line_start)
                            intersect_end = min(start + length, line_end)
                            
                            if intersect_start < intersect_end:
                                x1 = line.cursorToX(intersect_start)[0]
                                x2 = line.cursorToX(intersect_end)[0]
                                
                                doc_layout = self.document().documentLayout()
                                block_rect = doc_layout.blockBoundingRect(block)
                                b_pos = block_rect.topLeft()
                                
                                x_offset = self.horizontalScrollBar().value()
                                y_offset = self.verticalScrollBar().value()
                                
                                vx1 = b_pos.x() + x1 - x_offset
                                vx2 = b_pos.x() + x2 - x_offset
                                vy = b_pos.y() + line.y() - y_offset
                                vh = line.height()
                                
                                pad_x = 2
                                pad_y = 1
                                rect = QRectF(vx1 - pad_x, vy - pad_y, (vx2 - vx1) + (pad_x * 2), vh + (pad_y * 2))
                                
                                event_pos = event.position() if hasattr(event, 'position') else QPointF(event.pos())
                                if rect.contains(event_pos):
                                    clicked_on_box = True
                                    break
                                    
                        if clicked_on_box:
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
    def __init__(self, text_content, title, color):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Fix window transparency
        self.resize(350, 250)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) # Prevent edge resize cursor from overlapping buttons
        
        # Wrapping widget to hold border and background
        self.bg_widget = QWidget(self)
        color_name = color.name() if color and color.isValid() else "#E5E7EB"
        self.bg_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255, 255, 255, 240);
                border: 2px solid {color_name};
                border-radius: 12px;
            }}
        """)
        bg_layout = QVBoxLayout(self.bg_widget)
        bg_layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.bg_widget)
        
        # Header with title and close button
        header = QHBoxLayout()
        
        # Folder Title
        lbl_title = BodyLabel(title)
        lbl_title.setStyleSheet(f"""
            QLabel {{
                color: black;
                font-size: 12pt;
                border: 1px solid {color_name};
                border-radius: 4px;
                padding: 2px 6px;
                background-color: transparent;
            }}
        """)
        header.addWidget(lbl_title)
        header.addStretch()
        
        # Close Button
        btn_close = QPushButton("×") # Standard QPushButton for simpler styling
        btn_close.setFixedSize(24, 24)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                color: #555555;
                font-weight: bold;
                font-size: 16px;
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                color: black;
            }
        """)
        btn_close.clicked.connect(self.close)
        header.addWidget(btn_close)
        bg_layout.addLayout(header)
        
        # Re-use CustomTextEditor
        self.text_display = CustomTextEditor()
        self.text_display.setReadOnly(True)
        # Remove borders and focus lines
        self.text_display.setStyleSheet("TextEdit { border: none; background-color: transparent; } TextEdit:focus { border: none; }")
        self.text_display.setHtml(text_content)
        bg_layout.addWidget(self.text_display)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if hasattr(self, '_drag_position'):
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()


class VibeCodeThisWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe_Code-This")
        self.setGeometry(100, 100, 1200, 700)
        self.unsaved_changes = False
        self.workspace_path = get_workspace_path("workspace.json")
        self.init_ui()
        self.load_workspace()

    def init_ui(self):

        # Set macOS style fluent theme
        setTheme(Theme.LIGHT)
        setThemeColor('#004B87') # Dark blue from logo
        self.setStyleSheet("""
            VibeCodeThisWindow {
                background-color: #F3F4F6; /* Slightly darker light mode bg to make cards pop */
            }
            #Col1Widget, #Col2Widget, #Col3Widget {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
            #Col1Widget, #Col2Widget, #Col3Widget {
                margin: 4px; /* Add some spacing around the cards inside the splitter */
            }
        """)
        # FramelessWindow is a QWidget, so we use its layout directly
        # Also leave margin at the top for the title bar/macOS traffic lights
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 40, 10, 10)
        
        self.top_row_layout = QHBoxLayout()
        self.btn_import = PushButton("Restore Backup")
        self.btn_save_as = PushButton("Backup Workspace")
        self.lbl_selected_folder = SubtitleLabel("Select a folder")
        self.lbl_selected_folder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_selected_folder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                border: 3px solid #CCCCCC;
                border-radius: 6px;
                padding: 6px 16px;
                background-color: #FAFAFA;
                color: #777777;
            }
        """)
        self.btn_close = PushButton("Close")
        
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
        self.col1_widget.setObjectName("Col1Widget")
        self.col1_layout = QVBoxLayout(self.col1_widget)
        self.col1_header = QHBoxLayout()
        self.lbl_col1 = SubtitleLabel("Folders")
        self.btn_add_folder = TransparentPushButton("+")
        self.col1_header.addWidget(self.lbl_col1)
        self.col1_header.addStretch()
        self.col1_header.addWidget(self.btn_add_folder)
        
        self.tree_folders = TreeWidget()
        self.tree_folders.setHeaderHidden(True)
        self.tree_folders.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.tree_folders.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_folders.customContextMenuRequested.connect(self.show_folder_context_menu)
        self.tree_folders.currentItemChanged.connect(self.on_folder_selected)
        self.tree_folders.model().rowsMoved.connect(self.mark_unsaved)
        self.btn_add_folder.clicked.connect(self.add_folder)
        
        self.search_box = SearchLineEdit()
        self.search_box.setPlaceholderText("Search folders, tasks, notes...")
        self.search_box.textChanged.connect(self.perform_search)
        
        self.search_results = QTextBrowser()
        self.search_results.setOpenLinks(False)
        self.search_results.anchorClicked.connect(self.on_search_result_clicked)
        self.search_results.setStyleSheet("QTextBrowser { border: 1px solid #e0e0e0; border-radius: 6px; background-color: #fafafa; padding: 4px; }")
        self.search_results.hide()
        
        self.col1_layout.addLayout(self.col1_header)
        self.col1_layout.addWidget(self.tree_folders)
        self.col1_layout.addWidget(self.search_results)
        self.col1_layout.addWidget(self.search_box)
        
        # Column 2
        self.col2_widget = QWidget()
        self.col2_widget.setObjectName("Col2Widget")
        self.col2_layout = QVBoxLayout(self.col2_widget)
        self.col2_header = QHBoxLayout()
        self.lbl_col2 = SubtitleLabel("Tasks")
        self.btn_add_task = TransparentPushButton("+")
        self.col2_header.addWidget(self.lbl_col2)
        self.col2_header.addStretch()
        self.col2_header.addWidget(self.btn_add_task)
        
        self.list_tasks = ListWidget()
        self.list_tasks.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_tasks.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_tasks.setStyleSheet("""
            QListWidget::item {
                border-bottom: 1px solid #E5E5E5;
                padding: 8px 6px;
            }
            QListWidget::item:selected {
                background-color: #F0F0F0;
                border-radius: 4px;
                color: black;
            }
        """)
        self.btn_add_task.clicked.connect(self.add_task)
        self.list_tasks.currentItemChanged.connect(self.on_task_selected)
        self.list_tasks.customContextMenuRequested.connect(self.show_task_context_menu)
        self.list_tasks.model().rowsMoved.connect(lambda: self.save_current_folder_tasks(self.tree_folders.currentItem()))
        
        self.col2_layout.addLayout(self.col2_header)
        self.col2_layout.addWidget(self.list_tasks)
        
        # Column 3
        self.col3_widget = QWidget()
        self.col3_widget.setObjectName("Col3Widget")
        self.col3_layout = QVBoxLayout(self.col3_widget)
        self.col3_header = QHBoxLayout()
        self.btn_toggle_edit = PushButton("✏️")
        self.btn_trans = PushButton("Trans")
        
        self.col3_header.addWidget(self.btn_toggle_edit)
        self.col3_header.addStretch()
        self.col3_header.addWidget(self.btn_trans)
        
        # Formatting Toolbar
        self.formatting_widget = QWidget()
        self.format_layout = QHBoxLayout(self.formatting_widget)
        self.format_layout.setContentsMargins(0, 0, 0, 0)
        
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.change_font)
        self.format_layout.addWidget(self.font_combo)
        
        self.btn_bold = PushButton("B")
        self.btn_bold.setCheckable(True)
        self.btn_bold.clicked.connect(self.toggle_bold)
        self.format_layout.addWidget(self.btn_bold)
        
        self.btn_underline = PushButton("U")
        self.btn_underline.setCheckable(True)
        self.btn_underline.clicked.connect(self.toggle_underline)
        self.format_layout.addWidget(self.btn_underline)
        
        self.btn_center = PushButton("Center")
        self.btn_center.clicked.connect(self.align_center)
        self.format_layout.addWidget(self.btn_center)
        
        self.btn_bullet = PushButton("• List")
        self.btn_bullet.clicked.connect(self.insert_bullet)
        self.format_layout.addWidget(self.btn_bullet)
        
        self.btn_number = PushButton("1. List")
        self.btn_number.clicked.connect(self.insert_number)
        self.format_layout.addWidget(self.btn_number)
        
        self.btn_copy_block = PushButton("🔲 Copy")
        self.btn_copy_block.clicked.connect(self.format_as_copy_block)
        self.format_layout.addWidget(self.btn_copy_block)
        
        self.text_editor = CustomTextEditor()
        self.text_editor.setReadOnly(True)
        self.text_editor.setPlaceholderText("Select a task to view or edit notes...")
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

    def create_folder_icon(self, color):
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw the folder tab
        tab_path = QPainterPath()
        tab_path.addRoundedRect(QRectF(2, 2, 8, 5), 1.5, 1.5)
        
        # Main folder body
        body_path = QPainterPath()
        body_path.addRoundedRect(QRectF(1, 5, 18, 13), 2.0, 2.0)
        
        # Subtle premium gradient
        painter.setPen(Qt.PenStyle.NoPen)
        gradient = QLinearGradient(0, 2, 0, 18)
        gradient.setColorAt(0, color.lighter(115))
        gradient.setColorAt(1, color.darker(105))
        painter.setBrush(QBrush(gradient))
        
        # Draw tab and body
        painter.drawPath(tab_path)
        painter.drawPath(body_path)
        
        # Draw outline
        outline_pen = QPen(color.darker(120), 1)
        painter.setPen(outline_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(body_path)
        
        # Accent line
        painter.setPen(QPen(color.lighter(130), 1))
        painter.drawLine(2, 6, 18, 6)
        
        painter.end()
        return QIcon(pixmap)

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
        folder = self.tree_folders.currentItem()
        title = folder.text(0) if folder else "No Folder"
        color = folder.data(0, Qt.ItemDataRole.UserRole) if folder else None
        self.trans_win = TranslucentWindow(self.text_editor.toHtml(), title, color)
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


    def check_autosave(self):
        if self.unsaved_changes:
            self.save_workspace() # Saves to default workspace_path
            # Show a brief non-intrusive toast notification at the bottom
            InfoBar.success(
                title='Saved',
                content='Auto-saved to workspace',
                orient=Qt.Orientation.Horizontal,
                isClosable=False,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=1500,
                parent=self
            )

    def save_workspace(self, filepath=None):
        if filepath is None:
            filepath = self.workspace_path
            
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
            
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            self.unsaved_changes = False
        except Exception as e:
            # Fallback to home directory if write fails (e.g. read-only folder)
            fallback_path = os.path.join(os.path.expanduser("~"), "vibe_workspace.json")
            try:
                with open(fallback_path, 'w') as f:
                    json.dump(data, f, indent=4)
                self.unsaved_changes = False
                print(f"Warning: Could not save to {filepath} due to {e}. Saved fallback to {fallback_path}")
            except Exception:
                pass

    def load_workspace(self, filepath=None):
        if filepath is None:
            filepath = self.workspace_path
            
        if not os.path.exists(filepath):
            # Try to load from home directory fallback if default doesn't exist
            fallback_path = os.path.join(os.path.expanduser("~"), "vibe_workspace.json")
            if os.path.exists(fallback_path):
                filepath = fallback_path
            else:
                return
                
        try:
            with open(filepath, 'r') as f:
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
            self.apply_color_to_folder(item, color)
        else:
            self.apply_color_to_folder(item, QColor("#004B87"))
        
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
            dialog = FolderColorDialog(self)
            color = None
            if dialog.exec():
                color = dialog.getColor()
            parent = self.tree_folders.invisibleRootItem()
            item = QTreeWidgetItem(parent)
            item.setText(0, name)
            if color and color.isValid():
                self.apply_color_to_folder(item, color)
            else:
                self.apply_color_to_folder(item, QColor("#004B87"))
            self.mark_unsaved()

    def apply_color_to_folder(self, item, color):
        item.setData(0, Qt.ItemDataRole.UserRole, color)
        item.setForeground(0, color)
        item.setIcon(0, self.create_folder_icon(color))
        for i in range(item.childCount()):
            self.apply_color_to_folder(item.child(i), color)
        
        if item == self.tree_folders.currentItem():
            self.update_cascading_color(color)
        self.mark_unsaved()

    def update_cascading_color(self, color):
        color_name = color.name() if color and color.isValid() else "transparent"
        for i in range(self.list_tasks.count()):
            self.list_tasks.item(i).setForeground(color if color and color.isValid() else Qt.GlobalColor.black)
        
        border_style = f"2px solid {color_name}" if color_name != "transparent" else "1px solid #E5E7EB"
        base_style = "background-color: #FFFFFF; border-radius: 12px; margin: 4px;"
        
        self.col1_widget.setStyleSheet(f"#Col1Widget {{ {base_style} border: {border_style}; }}")
        self.col2_widget.setStyleSheet(f"#Col2Widget {{ {base_style} border: {border_style}; }}")
        self.col3_widget.setStyleSheet(f"#Col3Widget {{ {base_style} border: {border_style}; }}")
        # Update self.lbl_selected_folder style dynamically to match the color!
        border_color = color.name() if color and color.isValid() else "#CCCCCC"
        self.lbl_selected_folder.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                border: 3px solid {border_color};
                border-radius: 6px;
                padding: 6px 16px;
                background-color: #FAFAFA;
                color: #333333;
            }}
        """)
        
        sel_border = f"1px solid {color_name}" if color_name != "transparent" else "1px solid transparent"
        self.list_tasks.setStyleSheet(f"""
            QListWidget::item {{
                border-bottom: 1px solid #E5E5E5;
                padding: 8px 6px;
            }}
            QListWidget::item:selected {{
                background-color: #F0F0F0;
                border: {sel_border};
                border-radius: 4px;
                color: black;
            }}
        """)
        
        self.tree_folders.setStyleSheet(f"""
            QTreeWidget::item:selected {{
                background-color: #F0F0F0;
                border: {sel_border};
                border-radius: 4px;
                color: black;
            }}
        """)

    def perform_search(self, text):
        if not text.strip():
            self.search_results.hide()
            self.tree_folders.show()
            self.search_results.clear()
            return
            
        self.tree_folders.hide()
        self.search_results.show()
        
        text = text.lower()
        html = ["<div style='font-family: sans-serif; font-size: 13px;'>"]
        
        def get_item_path(item):
            path = []
            curr = item
            while curr:
                parent = curr.parent()
                if parent:
                    path.insert(0, str(parent.indexOfChild(curr)))
                    curr = parent
                else:
                    path.insert(0, str(self.tree_folders.invisibleRootItem().indexOfChild(curr)))
                    break
            return "-".join(path)

        def get_item_name_path(item):
            path = []
            curr = item
            while curr:
                path.insert(0, curr.text(0))
                curr = curr.parent()
            return " / ".join(path)

        def highlight(content, keyword):
            import re
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            return pattern.sub(lambda m: f"<span style='background-color: #00E5FF; color: black; border-radius: 3px; font-weight: bold;'>{m.group(0)}</span>", content)

        def search_item(item):
            item_path = get_item_path(item)
            item_name_path = get_item_name_path(item)
            
            # Check folder name
            if text in item.text(0).lower():
                html.append(f"<p><a href='folder:{item_path}' style='color: #333; text-decoration: none;'>📁 {highlight(item_name_path, text)}</a></p>")
                
            # Check tasks
            tasks = item.data(0, Qt.ItemDataRole.UserRole + 1) or []
            for task_idx, t in enumerate(tasks):
                task_name = t.get("name", "")
                task_note = t.get("note", "")
                
                # Strip HTML from note
                import re
                plain_note = re.sub(r'<[^>]+>', '', task_note)
                plain_note = plain_note.replace('&nbsp;', ' ').strip()
                
                if text in task_name.lower():
                    html.append(f"<p style='margin-left: 15px;'><a href='task:{item_path}:{task_idx}' style='color: #333; text-decoration: none;'>✅ {item_name_path} / <b>{highlight(task_name, text)}</b></a></p>")
                elif text in plain_note.lower():
                    # Generate a snippet
                    idx = plain_note.lower().find(text)
                    start = max(0, idx - 30)
                    end = min(len(plain_note), idx + len(text) + 30)
                    snippet = plain_note[start:end]
                    if start > 0: snippet = "..." + snippet
                    if end < len(plain_note): snippet = snippet + "..."
                    
                    html.append(f"<p style='margin-left: 15px;'><a href='task:{item_path}:{task_idx}' style='color: #333; text-decoration: none;'>📄 {item_name_path} / {task_name}<br><i style='color: #666;'>{highlight(snippet, text)}</i></a></p>")
            
            for i in range(item.childCount()):
                search_item(item.child(i))

        root = self.tree_folders.invisibleRootItem()
        for i in range(root.childCount()):
            search_item(root.child(i))
            
        html.append("</div>")
        if len(html) == 2: # only div tags
            html.insert(1, "<p style='color: #999; font-style: italic;'>No results found.</p>")
            
        self.search_results.setHtml("".join(html))

    def on_search_result_clicked(self, url):
        href = url.toString()
        parts = href.split(":")
        action = parts[0]
        item_path = parts[1]
        
        indices = [int(x) for x in item_path.split("-")]
        curr = self.tree_folders.invisibleRootItem()
        for idx in indices:
            curr = curr.child(idx)
            
        if not curr: return
        
        # Clear search which resets views
        self.search_box.clear()
        
        # Make sure parents are expanded
        parent = curr.parent()
        while parent:
            parent.setExpanded(True)
            parent = parent.parent()
            
        self.tree_folders.setCurrentItem(curr)
        
        if action == "task" and len(parts) > 2:
            task_idx = int(parts[2])
            if task_idx < self.list_tasks.count():
                self.list_tasks.setCurrentRow(task_idx)

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
                if color:
                    self.apply_color_to_folder(new_item, color)
                else:
                    self.apply_color_to_folder(new_item, QColor("#004B87"))
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
            dialog = FolderColorDialog(self)
            if dialog.exec():
                color = dialog.getColor()
                if color and color.isValid():
                    self.apply_color_to_folder(item, color)

    def show_task_context_menu(self, pos):
        item = self.list_tasks.itemAt(pos)
        if not item: return
        menu = QMenu()
        a_rename = menu.addAction("Rename")
        a_dup = menu.addAction("Duplicate")
        a_del = menu.addAction("Delete")
        
        action = menu.exec(self.list_tasks.mapToGlobal(pos))
        folder = self.tree_folders.currentItem()
        if not folder: return
        
        if action == a_rename:
            name, ok = QInputDialog.getText(self, "Rename Task", "Task Name:", text=item.text())
            if ok and name:
                item.setText(name)
                self.save_current_folder_tasks(folder)
        elif action == a_dup:
            new_item = QListWidgetItem(item.text() + " (copy)")
            new_item.setData(Qt.ItemDataRole.UserRole, item.data(Qt.ItemDataRole.UserRole))
            c = item.foreground().color()
            if c.isValid():
                new_item.setForeground(c)
            self.list_tasks.addItem(new_item)
            self.list_tasks.setCurrentItem(new_item)
            self.save_current_folder_tasks(folder)
        elif action == a_del:
            if QMessageBox.question(self, "Confirm", "Delete task?") == QMessageBox.StandardButton.Yes:
                self.list_tasks.takeItem(self.list_tasks.row(item))
                self.save_current_folder_tasks(folder)

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
        self.lbl_selected_folder.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                border: 3px solid #CCCCCC;
                border-radius: 6px;
                padding: 6px 16px;
                background-color: #FAFAFA;
                color: #777777;
            }
        """)
        
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
        if not self.list_tasks.currentItem():
            return
        new_state = not self.text_editor.isReadOnly()
        self.text_editor.setReadOnly(new_state)
        self.formatting_widget.setVisible(not new_state)

    def save_task_note(self):
        item = self.list_tasks.currentItem()
        if item:
            item.setData(Qt.ItemDataRole.UserRole, self.text_editor.toHtml())
            self.save_current_folder_tasks(self.tree_folders.currentItem())

    def closeEvent(self, event):
        # Safely close translucent helper window if open to avoid thread crashes on exit
        if hasattr(self, 'trans_win') and self.trans_win:
            try:
                self.trans_win.close()
            except Exception:
                pass
                
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
