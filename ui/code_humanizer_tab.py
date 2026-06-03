"""
Aether Code Humanizer – Make code feel human-written
Supports single files or entire folders with batch processing
"""

import re
import random
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QSplitter, QMessageBox, QApplication,
    QProgressBar, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QGroupBox, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QAction, QKeySequence
from PySide6.QtCore import Qt, QThread, Signal


class HumanizerWorker(QThread):
    """Background thread for batch humanization"""
    progress = Signal(int)
    file_done = Signal(str, str)  # file path, status
    finished = Signal()
    log = Signal(str)
    
    def __init__(self, files, rules):
        super().__init__()
        self.files = files
        self.rules = rules
    
    def run(self):
        total = len(self.files)
        for idx, file_path in enumerate(self.files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                humanized = self.apply_rules(code)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(humanized)
                
                self.file_done.emit(str(file_path), "Done")
                self.log.emit(f"Humanized: {file_path.name}")
            except Exception as e:
                self.file_done.emit(str(file_path), f"Error: {str(e)[:30]}")
                self.log.emit(f"Error: {file_path.name} - {str(e)}")
            
            self.progress.emit(int((idx + 1) / total * 100))
        
        self.finished.emit()
    
    def apply_rules(self, code):
        """Apply humanization rules to code"""
        lines = code.split('\n')
        new_lines = []
        comment_count = 0
        emotional_phrases = [
            "idk why this works but",
            "lol don't ask",
            "this is cursed but",
            "TODO: figure out why",
            "somebody please refactor this",
            "works on my machine",
            "i have no idea what this does",
            "dont touch this line ever",
            "this is why we cant have nice things",
            "i hate this but it works",
            "temporary solution",
            "spaghetti code"
        ]
        
        for line in lines:
            # Remove obvious comments that just repeat the code
            if '=' in line and '# assign' in line.lower():
                continue
            if 'return' in line and '# return' in line.lower():
                continue
            if 'for' in line and '# iterate' in line.lower():
                continue
            
            # Lowercase comments (except those with *)
            if '#' in line and '*' not in line:
                comment_start = line.find('#')
                before_comment = line[:comment_start]
                comment = line[comment_start:]
                comment = comment.lower()
                comment = comment.rstrip('.')
                line = before_comment + comment
            
            # Add emotional comments randomly
            if comment_count < self.rules.get('max_comments', 2) and '#' in line and random.random() < 0.15:
                phrase = random.choice(emotional_phrases)
                line = line + f"  # {phrase}"
                comment_count += 1
            
            # Random whitespace
            if random.random() < 0.03 and len(new_lines) > 0:
                new_lines.append('')
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)


class CodeHumanizerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.comment_positions = []
        self.current_comment_index = -1
        self.batch_files = []
        self.humanizer_worker = None
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Mode selection
        mode_group = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        self.single_mode = QRadioButton("Single File")
        self.single_mode.setChecked(True)
        self.batch_mode = QRadioButton("Batch Folder")
        self.single_mode.toggled.connect(self.on_mode_changed)
        mode_layout.addWidget(self.single_mode)
        mode_layout.addWidget(self.batch_mode)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Single file controls
        self.single_widget = QWidget()
        single_layout = QHBoxLayout(self.single_widget)
        self.open_btn = QPushButton("Open File")
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn = QPushButton("Save Humanized Version")
        self.save_btn.clicked.connect(self.save_file)
        self.copy_to_right_btn = QPushButton("Copy Left to Right")
        self.copy_to_right_btn.clicked.connect(self.copy_left_to_right)
        self.apply_all_btn = QPushButton("Apply to Left")
        self.apply_all_btn.clicked.connect(self.apply_to_left)
        single_layout.addWidget(self.open_btn)
        single_layout.addWidget(self.save_btn)
        single_layout.addWidget(self.copy_to_right_btn)
        single_layout.addWidget(self.apply_all_btn)
        layout.addWidget(self.single_widget)

        # Batch controls
        self.batch_widget = QWidget()
        self.batch_widget.setVisible(False)
        batch_layout = QVBoxLayout(self.batch_widget)
        
        batch_controls = QHBoxLayout()
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.batch_humanize_btn = QPushButton("Batch Humanize All Files")
        self.batch_humanize_btn.clicked.connect(self.batch_humanize)
        self.batch_humanize_btn.setEnabled(False)
        batch_controls.addWidget(self.select_folder_btn)
        batch_controls.addWidget(self.batch_humanize_btn)
        batch_layout.addLayout(batch_controls)
        
        self.folder_label = QLabel("No folder selected")
        batch_layout.addWidget(self.folder_label)
        
        # File list for batch
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["File", "Status"])
        self.file_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.file_tree.setMaximumHeight(150)
        batch_layout.addWidget(self.file_tree)
        
        layout.addWidget(self.batch_widget)

        # Automate button (for single file)
        self.automate_btn = QPushButton("Automate Humanize")
        self.automate_btn.clicked.connect(self.humanize_code)
        layout.addWidget(self.automate_btn)

        # Split editor
        self.splitter = QSplitter(Qt.Horizontal)
        
        self.left_editor = QPlainTextEdit()
        self.left_editor.setFont(QFont("Courier New", 10))
        self.left_editor.setPlaceholderText("Original code (editable)")
        
        self.right_editor = QPlainTextEdit()
        self.right_editor.setFont(QFont("Courier New", 10))
        self.right_editor.setPlaceholderText("Humanized code will appear here (editable)")
        self.right_editor.textChanged.connect(self.on_right_text_changed)
        
        self.splitter.addWidget(self.left_editor)
        self.splitter.addWidget(self.right_editor)
        layout.addWidget(self.splitter)

        # Navigation bar
        nav_bar = QHBoxLayout()
        self.prev_btn = QPushButton("Prev Comment")
        self.prev_btn.clicked.connect(self.prev_comment)
        self.next_btn = QPushButton("Next Comment")
        self.next_btn.clicked.connect(self.next_comment)
        self.comment_counter = QLabel("No comments")
        nav_bar.addWidget(self.prev_btn)
        nav_bar.addWidget(self.next_btn)
        nav_bar.addWidget(self.comment_counter)
        nav_bar.addStretch()
        layout.addLayout(nav_bar)

        # Progress bar (for batch)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Status
        self.status_label = QLabel("Ready - Select a file or folder to start")
        layout.addWidget(self.status_label)

    def on_mode_changed(self):
        """Toggle between single file and batch mode"""
        is_single = self.single_mode.isChecked()
        self.single_widget.setVisible(is_single)
        self.batch_widget.setVisible(not is_single)
        self.automate_btn.setVisible(is_single)
        self.splitter.setVisible(is_single)
        nav_bar_visible = is_single and len(self.comment_positions) > 0
        self.prev_btn.setVisible(nav_bar_visible)
        self.next_btn.setVisible(nav_bar_visible)
        self.comment_counter.setVisible(nav_bar_visible)

    def setup_shortcuts(self):
        """Setup undo/redo shortcuts"""
        self.undo_left = QAction(self)
        self.undo_left.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_left.triggered.connect(self.left_editor.undo)
        self.addAction(self.undo_left)
        
        self.redo_left = QAction(self)
        self.redo_left.setShortcut(QKeySequence("Ctrl+Y"))
        self.redo_left.triggered.connect(self.left_editor.redo)
        self.addAction(self.redo_left)
        
        self.undo_right = QAction(self)
        self.undo_right.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        self.undo_right.triggered.connect(self.right_editor.undo)
        self.addAction(self.undo_right)
        
        self.redo_right = QAction(self)
        self.redo_right.setShortcut(QKeySequence("Ctrl+Shift+Y"))
        self.redo_right.triggered.connect(self.right_editor.redo)
        self.addAction(self.redo_right)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Code Files (*.py *.js *.html *.css *.ts *.tsx *.jsx);;All Files (*.*)"
        )
        if path:
            self.current_file = path
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.left_editor.setPlainText(content)
            self.right_editor.clear()
            self.status_label.setText(f"Opened: {path}")

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.right_editor.toPlainText())
            self.status_label.setText(f"Saved humanized version to: {self.current_file}")
        else:
            self.save_as()

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Code Files (*.py *.js *.html *.css);;All Files (*.*)")
        if path:
            self.current_file = path
            self.save_file()

    def copy_left_to_right(self):
        self.right_editor.setPlainText(self.left_editor.toPlainText())
        self.status_label.setText("Copied original to right panel")

    def apply_to_left(self):
        self.left_editor.setPlainText(self.right_editor.toPlainText())
        self.status_label.setText("Applied humanized version to left panel")

    def on_right_text_changed(self):
        self.scan_comments()

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder with Code Files")
        if path:
            self.folder_label.setText(path)
            self.batch_files = []
            self.file_tree.clear()
            
            # Find all code files
            extensions = ['*.py', '*.js', '*.html', '*.css', '*.ts', '*.tsx', '*.jsx']
            for ext in extensions:
                self.batch_files.extend(Path(path).rglob(ext))
            
            for file_path in self.batch_files:
                rel_path = file_path.relative_to(path)
                item = QTreeWidgetItem([str(rel_path), "Pending"])
                item.setData(0, Qt.UserRole, str(file_path))
                self.file_tree.addTopLevelItem(item)
            
            self.batch_humanize_btn.setEnabled(len(self.batch_files) > 0)
            self.status_label.setText(f"Found {len(self.batch_files)} files to humanize")

    def batch_humanize(self):
        if not self.batch_files:
            QMessageBox.warning(self, "Warning", "No files selected. Select a folder first.")
            return
        
        reply = QMessageBox.question(self, "Batch Humanize",
                                     f"Humanize {len(self.batch_files)} files?\n\n"
                                     f"This will modify the original files. Backup recommended.\n\n"
                                     f"Proceed?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        self.batch_humanize_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        rules = {'max_comments': 2}
        
        self.humanizer_worker = HumanizerWorker(self.batch_files, rules)
        self.humanizer_worker.progress.connect(self.update_batch_progress)
        self.humanizer_worker.file_done.connect(self.update_file_status)
        self.humanizer_worker.finished.connect(self.on_batch_finished)
        self.humanizer_worker.log.connect(self.status_label.setText)
        self.humanizer_worker.start()
        
        self.status_label.setText("Batch humanization in progress...")

    def update_batch_progress(self, value):
        self.progress.setValue(value)

    def update_file_status(self, file_path, status):
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == file_path:
                item.setText(1, status)
                if "Done" in status:
                    item.setForeground(1, Qt.GlobalColor(Qt.darkGreen))
                elif "Error" in status:
                    item.setForeground(1, Qt.GlobalColor(Qt.red))
                break

    def on_batch_finished(self):
        self.progress.setVisible(False)
        self.batch_humanize_btn.setEnabled(True)
        self.status_label.setText("Batch humanization complete!")
        QMessageBox.information(self, "Batch Complete", "All files have been humanized!")

    # ========== SINGLE FILE HUMANIZATION ==========

    def humanize_code(self):
        code = self.left_editor.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, "Warning", "No code to humanize.")
            return
        
        self.status_label.setText("Humanizing code...")
        QApplication.processEvents()
        
        humanized = self.apply_humanization_rules(code)
        self.right_editor.setPlainText(humanized)
        self.scan_comments()
        self.status_label.setText("Humanization complete!")
        
        QMessageBox.information(self, "Done", "Code has been humanized!\n\n"
                                "You can now:\n"
                                "- Edit the result manually\n"
                                "- Navigate comments with Prev/Next\n"
                                "- Apply to left or save as new file")

    def apply_humanization_rules(self, code):
        lines = code.split('\n')
        new_lines = []
        comment_count = 0
        emotional_phrases = [
            "idk why this works but",
            "lol don't ask",
            "this is cursed but",
            "TODO: figure out why",
            "somebody please refactor this",
            "works on my machine",
            "i have no idea what this does",
            "dont touch this line ever",
            "this is why we cant have nice things",
            "i hate this but it works",
            "temporary solution",
            "spaghetti code"
        ]
        
        for line in lines:
            if '=' in line and '# assign' in line.lower():
                continue
            if 'return' in line and '# return' in line.lower():
                continue
            if 'for' in line and '# iterate' in line.lower():
                continue
            
            if '#' in line and '*' not in line:
                comment_start = line.find('#')
                before_comment = line[:comment_start]
                comment = line[comment_start:]
                comment = comment.lower()
                comment = comment.rstrip('.')
                line = before_comment + comment
            
            if comment_count < 2 and '#' in line and random.random() < 0.15:
                phrase = random.choice(emotional_phrases)
                line = line + f"  # {phrase}"
                comment_count += 1
            
            if random.random() < 0.03 and len(new_lines) > 0:
                new_lines.append('')
            
            new_lines.append(line)
        
        return '\n'.join(new_lines)

    def scan_comments(self):
        text = self.right_editor.toPlainText()
        self.comment_positions = []
        
        lines = text.split('\n')
        for line_num, line in enumerate(lines):
            hash_pos = line.find('#')
            if hash_pos != -1:
                if not (line_num == 0 and line.startswith('#!')):
                    self.comment_positions.append({
                        'line': line_num,
                        'char': hash_pos,
                        'text': line[hash_pos:].strip()
                    })
            
            comment_start = line.find('<!--')
            if comment_start != -1:
                self.comment_positions.append({
                    'line': line_num,
                    'char': comment_start,
                    'text': line[comment_start:].strip()[:50]
                })
        
        has_comments = len(self.comment_positions) > 0
        self.prev_btn.setVisible(has_comments)
        self.next_btn.setVisible(has_comments)
        self.comment_counter.setVisible(has_comments)
        self.comment_counter.setText(f"{len(self.comment_positions)} comment(s)")

    def goto_comment(self, index):
        if not self.comment_positions or index < 0 or index >= len(self.comment_positions):
            return
        
        self.current_comment_index = index
        comment = self.comment_positions[index]
        
        cursor = self.right_editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, comment['line'])
        cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, comment['char'])
        
        cursor.select(QTextCursor.LineUnderCursor)
        
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(255, 255, 100))
        cursor.mergeCharFormat(fmt)
        
        from PySide6.QtCore import QTimer
        def clear_highlight():
            cursor.setCharFormat(QTextCharFormat())
        QTimer.singleShot(1000, clear_highlight)
        
        self.right_editor.setTextCursor(cursor)
        self.right_editor.ensureCursorVisible()
        
        self.comment_counter.setText(f"Comment {self.current_comment_index + 1} of {len(self.comment_positions)}")

    def prev_comment(self):
        if self.comment_positions:
            new_index = self.current_comment_index - 1
            if new_index < 0:
                new_index = len(self.comment_positions) - 1
            self.goto_comment(new_index)

    def next_comment(self):
        if self.comment_positions:
            new_index = self.current_comment_index + 1
            if new_index >= len(self.comment_positions):
                new_index = 0
            self.goto_comment(new_index)

    def update_theme(self, is_dark):
        if is_dark:
            # Editor backgrounds
            self.left_editor.setStyleSheet("background-color: #2B2D31; color: #E8E8E8;")
            self.right_editor.setStyleSheet("background-color: #2B2D31; color: #E8E8E8;")
            
            # File tree
            self.file_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    alternate-background-color: #3E4045;
                }
                QHeaderView::section {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
            """)
            
            # Main widget styling (fixes radio buttons)
            self.setStyleSheet("""
                QGroupBox {
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                    margin-top: 10px;
                    background-color: transparent;
                }
                QGroupBox::title {
                    color: #E8E8E8;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QRadioButton {
                    color: #E8E8E8;
                    spacing: 8px;
                    background-color: transparent;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                }
                QLabel {
                    color: #E8E8E8;
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #8095AB;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: #1E1F22;
                }
                QPlainTextEdit {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
                QWidget {
                    background-color: transparent;
                }
            """)
        else:
            # Editor backgrounds
            self.left_editor.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")
            self.right_editor.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")
            
            # File tree
            self.file_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    alternate-background-color: #F8F9FA;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
            
            # Main widget styling
            self.setStyleSheet("""
                QGroupBox {
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                    margin-top: 10px;
                    background-color: transparent;
                }
                QGroupBox::title {
                    color: #2C3E50;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QRadioButton {
                    color: #2C3E50;
                    spacing: 8px;
                    background-color: transparent;
                }
                QLabel {
                    color: #2C3E50;
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #E9ECF1;
                    color: #2C3E50;
                    border: 1px solid #8095AB;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: white;
                }
                QPlainTextEdit {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
                QWidget {
                    background-color: transparent;
                }
            """)