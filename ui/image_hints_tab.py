import os
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QCheckBox, QTreeWidget, QTreeWidgetItem, QHeaderView, QApplication
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class ImageHintsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for Image Issues")
        self.scan_btn.clicked.connect(self.scan_images)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Options
        opts_group = QGroupBox("Scan Options")
        opts_layout = QHBoxLayout()
        self.check_missing_dimensions = QCheckBox("Missing width/height attributes")
        self.check_missing_dimensions.setChecked(True)
        self.check_oversized = QCheckBox("Oversized images (>2x display size)")
        self.check_oversized.setChecked(True)
        opts_layout.addWidget(self.check_missing_dimensions)
        opts_layout.addWidget(self.check_oversized)
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Issue Type", "File", "Image", "Details"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.results_tree)

        # Summary
        self.summary_label = QLabel("Ready - Select a folder and click Scan")
        layout.addWidget(self.summary_label)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def log_msg(self, msg):
        self.summary_label.setText(msg)
        QApplication.processEvents()

    def scan_images(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.log_msg("No HTML files found.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_tree.clear()
        self.results = []

        missing_dim_count = 0
        oversized_count = 0

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))

                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    if not src:
                        continue

                    # Resolve image path
                    img_path = None
                    if src.startswith('http'):
                        # Skip external images for now (can't check dimensions)
                        continue
                    else:
                        # Try relative path
                        candidate = html_path.parent / src
                        if candidate.exists():
                            img_path = candidate
                        else:
                            candidate = Path(self.project_folder) / src
                            if candidate.exists():
                                img_path = candidate

                    # 1. Check missing width/height attributes
                    if self.check_missing_dimensions.isChecked():
                        has_width = img.get('width') is not None
                        has_height = img.get('height') is not None
                        if not has_width or not has_height:
                            missing_dim_count += 1
                            self._add_result("Missing dimensions", rel_path, src,
                                           f"Add width and height attributes to prevent layout shift (CLS)")

                    # 2. Check oversized images
                    if self.check_oversized.isChecked() and img_path and img_path.exists():
                        try:
                            with Image.open(img_path) as pil_img:
                                actual_w, actual_h = pil_img.size
                                
                                # Get displayed size from attributes or styles
                                display_w = img.get('width')
                                display_h = img.get('height')
                                
                                if display_w:
                                    display_w = int(display_w)
                                elif img.get('style') and 'width' in img['style']:
                                    # Basic style parsing
                                    import re
                                    match = re.search(r'width:\s*(\d+)', img['style'])
                                    display_w = int(match.group(1)) if match else actual_w
                                else:
                                    display_w = actual_w
                                
                                if display_h:
                                    display_h = int(display_h)
                                elif img.get('style') and 'height' in img['style']:
                                    import re
                                    match = re.search(r'height:\s*(\d+)', img['style'])
                                    display_h = int(match.group(1)) if match else actual_h
                                else:
                                    display_h = actual_h
                                
                                # Check if image is oversized (>2x display size)
                                if actual_w > display_w * 2 or actual_h > display_h * 2:
                                    oversized_count += 1
                                    self._add_result("Oversized image", rel_path, src,
                                                   f"Image is {actual_w}x{actual_h} but displayed at ~{display_w}x{display_h}. "
                                                   f"Resize to ~{display_w}x{display_h} to save bandwidth.")
                        except Exception as e:
                            pass  # Skip images that can't be processed

            except Exception as e:
                self._add_result("Parse error", rel_path, "", str(e)[:100])

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)

        total = missing_dim_count + oversized_count
        self.log_msg(f"\uf00c Scan complete! Found {total} image issues across {len(html_files)} files.\n"
                     f"  • Missing width/height: {missing_dim_count}\n"
                     f"  • Oversized images: {oversized_count}")

        QMessageBox.information(self, "Scan Complete", 
                                f"Found {total} image issues.\n\n"
                                f"• Missing width/height: {missing_dim_count}\n"
                                f"  (Add these to prevent CLS - Cumulative Layout Shift)\n\n"
                                f"• Oversized images: {oversized_count}\n"
                                f"  (Resize images to reduce page weight)")

    def _add_result(self, issue_type, file_path, element, description):
        item = QTreeWidgetItem([issue_type, file_path, element, description])
        self.results_tree.addTopLevelItem(item)
        self.results.append({
            "type": issue_type,
            "file": file_path,
            "element": element,
            "description": description
        })

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    alternate-background-color: #3E4045;
                    background-color: #2B2D31;
                    color: #E8E8E8;
                }
                QHeaderView::section {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
            """)
        else:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    alternate-background-color: #F8F9FA;
                    background-color: #FFFFFF;
                    color: #2C3E50;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
