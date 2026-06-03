import os
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QApplication, QInputDialog
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup
import shutil

class WebPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.images_folder = None
        self.html_folder = None
        self.web_root = None  # local folder that corresponds to web root (e.g., for /assets/ paths)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # image source folder
        img_group = QGroupBox("1. Image Source Folder")
        img_layout = QHBoxLayout()
        self.img_label = QLabel("No folder selected")
        self.img_btn = QPushButton("Select Image Folder")
        self.img_btn.clicked.connect(self.select_images_folder)
        img_layout.addWidget(self.img_btn)
        img_layout.addWidget(self.img_label)
        img_layout.addStretch()
        img_group.setLayout(img_layout)
        layout.addWidget(img_group)

        # html project folder (optional)
        html_group = QGroupBox("2. HTML Project Folder (optional – to update image references)")
        html_layout = QHBoxLayout()
        self.html_label = QLabel("Not selected – will only convert images")
        self.html_btn = QPushButton("Select HTML Folder")
        self.html_btn.clicked.connect(self.select_html_folder)
        html_layout.addWidget(self.html_btn)
        html_layout.addWidget(self.html_label)
        html_layout.addStretch()
        html_group.setLayout(html_layout)
        layout.addWidget(html_group)

        # web root folder for resolving absolute paths (e.g., if src="/assets/...")
        webroot_group = QGroupBox("3. Web Root Folder (for absolute paths like /assets/)")
        webroot_layout = QHBoxLayout()
        self.webroot_label = QLabel("Same as HTML folder if not specified")
        self.webroot_btn = QPushButton("Select Web Root")
        self.webroot_btn.clicked.connect(self.select_web_root)
        webroot_layout.addWidget(self.webroot_btn)

        webroot_layout.addWidget(self.webroot_label)
        webroot_layout.addStretch()
        webroot_group.setLayout(webroot_layout)
        layout.addWidget(webroot_group)

        # conversion options
        opts_group = QGroupBox("4. Conversion Options")
        opts_layout = QFormLayout()

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 100)
        self.quality_spin.setValue(85)
        opts_layout.addRow("WebP quality (1-100):", self.quality_spin)
        self.lossless_check = QCheckBox("Lossless (ignores quality)")
        opts_layout.addRow(self.lossless_check)
        self.remove_original = QCheckBox("Delete original image after conversion")
        opts_layout.addRow(self.remove_original)
        self.suffix_edit = QLineEdit(".webp")
        opts_layout.addRow("Output suffix:", self.suffix_edit)
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # update html method
        method_group = QGroupBox("5. HTML Update Method (if HTML folder selected)")
        method_layout = QVBoxLayout()
        self.update_src_check = QCheckBox("Replace src attribute directly (.png → .webp)")
        self.update_src_check.setChecked(True)
        method_layout.addWidget(self.update_src_check)
        method_group.setLayout(method_layout)
        layout.addWidget(method_group)

        # progress and logs
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(200)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log)

        self.convert_btn = QPushButton("▶ Convert Images & Update HTML")

        self.convert_btn.clicked.connect(self.convert_and_update)
        layout.addWidget(self.convert_btn)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def select_images_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder with Images")
        if path:
            self.images_folder = path
            self.img_label.setText(path)
            self.log.appendPlainText(f"Image folder: {path}")


    def select_html_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder (with HTML files)")
        if path:
            self.html_folder = path
            self.html_label.setText(path)
            self.log.appendPlainText(f"HTML folder: {path}")

    def select_web_root(self):
        path = QFileDialog.getExistingDirectory(self, "Select Web Root Folder (e.g., where /assets/ maps to)")
        if path:
            self.web_root = path
            self.webroot_label.setText(path)
            self.log.appendPlainText(f"Web root: {path}")

    def log_msg(self, msg):
        self.log.appendPlainText(msg)

        QApplication.processEvents()

    def convert_and_update(self):
        if not self.images_folder or not os.path.isdir(self.images_folder):
            QMessageBox.warning(self, "Warning", "Please select a valid image source folder.")
            return

        extensions = (".jpg", ".jpeg", ".png")
        images = []
        for ext in extensions:

            images.extend(Path(self.images_folder).glob(f"*{ext}"))
            images.extend(Path(self.images_folder).glob(f"*{ext.upper()}"))
        if not images:
            QMessageBox.information(self, "Info", "No JPG or PNG images found.")
            return

        self.convert_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(images))
        self.log.clear()

        quality = self.quality_spin.value()
        lossless = self.lossless_check.isChecked()
        delete_original = self.remove_original.isChecked()
        suffix = self.suffix_edit.text().strip()
        if not suffix.startswith('.'):
            suffix = '.' + suffix


        converted_paths = {}  # absolute original path -> absolute webp path
        for idx, img_path in enumerate(images):
            try:
                img = Image.open(img_path)
                webp_path = img_path.with_suffix(suffix)
                if lossless:
                    img.save(webp_path, "WEBP", lossless=True)
                else:
                    img.save(webp_path, "WEBP", quality=quality)
                converted_paths[str(img_path.resolve())] = str(webp_path.resolve())

                self.log_msg(f"Converted: {img_path.name} → {webp_path.name}")
                if delete_original:
                    os.remove(img_path)
                    self.log_msg(f"  Deleted original: {img_path.name}")
            except Exception as e:
                self.log_msg(f"ERROR converting {img_path.name}: {e}")
            self.progress.setValue(idx + 1)

        # update html files if folder provided
        if self.html_folder and os.path.isdir(self.html_folder):
            self.update_html_files(converted_paths)

        self.progress.setVisible(False)
        self.convert_btn.setEnabled(True)
        QMessageBox.information(self, "Done", f"Converted {len(converted_paths)} images.\nCheck log for details.")
        self.status_label.setText("Conversion completed.")

    def update_html_files(self, converted_paths):
        """Replace img src .png/.jpg with .webp in all HTML files."""
        html_files = list(Path(self.html_folder).rglob("*.html"))
        if not html_files:
            self.log_msg("No HTML files found to update.")
            return


        if not self.update_src_check.isChecked():
            self.log_msg("HTML update not enabled – skipping.")
            return

        # determine base for absolute paths: if web_root is set, use it; otherwise use html_folder
        base_dir = self.web_root if self.web_root else self.html_folder
        if not base_dir:
            base_dir = self.html_folder
        base_dir = Path(base_dir).resolve()

        updated_count = 0

        img_extensions = ('.png', '.jpg', '.jpeg', '.JPG', '.JPEG', '.PNG')
        for html_path in html_files:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            modified = False
            for img in soup.find_all('img'):
                src = img.get('src')
                if not src:
                    continue
                # convert url to filesystem path
                if src.startswith('/'):
                    # absolute web path: /assets/img/ppp.png
                    # remove leading slash and join with base_dir
                    rel_path = src.lstrip('/')
                    fs_path = (base_dir / rel_path).resolve()
                else:
                    # relative path: resolve relative to html file location
                    fs_path = (html_path.parent / src).resolve()
                # check if this file was converted
                if str(fs_path) in converted_paths:
                    webp_abs_path = converted_paths[str(fs_path)]
                    # compute new src attribute: maintain same type of path (absolute/relative)  # i hate this but it works
                    if src.startswith('/'):
                        # absolute: compute new url by replacing extension
                        new_src = src.rsplit('.', 1)[0] + '.webp'
                    else:
                        # relative: compute new relative path from html to webp file
                        try:
                            new_src = os.path.relpath(webp_abs_path, html_path.parent)
                        except:
                            new_src = src.rsplit('.', 1)[0] + '.webp'
                    img['src'] = new_src
                    modified = True
                    self.log_msg(f"Updated {html_path.name}: {src} → {new_src}")
            if modified:

                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                updated_count += 1
        self.log_msg(f"Updated {updated_count} HTML files.")
