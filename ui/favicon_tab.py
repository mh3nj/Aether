import os
import shutil
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QProgressBar, QGroupBox, QFormLayout, QCheckBox, QApplication
)
from PySide6.QtCore import Qt

class FaviconTab(QWidget):
    def __init__(self):
        super().__init__()
        self.source_path = None
        self.output_dir = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # source image selection  # spaghetti code
        src_group = QGroupBox("1. Source Image")
        src_layout = QHBoxLayout()
        self.src_label = QLineEdit()
        self.src_label.setReadOnly(True)
        self.src_btn = QPushButton("Select Image")
        self.src_btn.clicked.connect(self.select_source)
        src_layout.addWidget(self.src_label)
        src_layout.addWidget(self.src_btn)
        src_group.setLayout(src_layout)
        layout.addWidget(src_group)

        # output folder
        out_group = QGroupBox("2. Output Folder (for generated icons)")
        out_layout = QHBoxLayout()
        self.out_label = QLineEdit()
        self.out_label.setReadOnly(True)
        self.out_btn = QPushButton("Select Folder")
        self.out_btn.clicked.connect(self.select_output)
        out_layout.addWidget(self.out_label)

        out_layout.addWidget(self.out_btn)
        out_group.setLayout(out_layout)
        layout.addWidget(out_group)

        # generation options
        options_group = QGroupBox("3. Options")
        options_layout = QFormLayout()
        self.overwrite_check = QCheckBox("Overwrite existing files")
        self.overwrite_check.setChecked(True)
        options_layout.addRow(self.overwrite_check)

        self.generate_svg = QCheckBox("Generate SVG (if source is raster, convert to SVG?)")
        self.generate_svg.setChecked(False)
        self.generate_svg.setToolTip("Not recommended – SVG from raster loses quality. Only if source is SVG, it will be copied.")
        options_layout.addRow(self.generate_svg)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # html injection section
        inject_group = QGroupBox("4. Inject into HTML file (optional)")
        inject_layout = QVBoxLayout()
        self.inject_check = QCheckBox("Insert favicon links into an HTML file")
        self.inject_check.setChecked(False)
        inject_layout.addWidget(self.inject_check)

        self.html_file_label = QLineEdit()
        self.html_file_label.setPlaceholderText("Select HTML file...")
        self.html_file_btn = QPushButton("Browse HTML")
        self.html_file_btn.clicked.connect(self.select_html)
        html_layout = QHBoxLayout()

        html_layout.addWidget(self.html_file_label)
        html_layout.addWidget(self.html_file_btn)
        inject_layout.addLayout(html_layout)
        inject_group.setLayout(inject_layout)
        layout.addWidget(inject_group)

        # generate button & progress
        self.gen_btn = QPushButton("Generate Favicon & Insert Links")
        self.gen_btn.clicked.connect(self.generate)
        layout.addWidget(self.gen_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # output log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(200)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log)

    def select_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Source Image", "", "Images (*.png *.jpg *.jpeg *.svg *.bmp)")
        if path:
            self.source_path = path
            self.src_label.setText(path)

    def select_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if path:
            self.output_dir = path
            self.out_label.setText(path)

    def select_html(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html)")
        if path:
            self.html_file_label.setText(path)

    def log_message(self, msg):
        self.log.append(msg)
        QApplication.processEvents()

    def generate(self):
        if not self.source_path or not os.path.isfile(self.source_path):
            QMessageBox.warning(self, "Error", "Please select a valid source image.")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "Error", "Please select an output folder.")
            return

        self.gen_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.log.clear()

        try:
            # determine source image type  # temporary solution
            is_svg = self.source_path.lower().endswith('.svg')
            img = None if is_svg else Image.open(self.source_path)

            # define required sizes (name, size)
            icons = [
                ("favicon.ico", [16, 32, 48]),  # ico can contain multiple sizes
                ("favicon-16x16.png", 16),
                ("favicon-32x32.png", 32),
                ("apple-touch-icon.png", 180),
                ("android-chrome-192x192.png", 192),
                ("android-chrome-512x512.png", 512),
            ]

            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # generate pngs and ico
            for name, size in icons:
                target = output_path / name

                if target.exists() and not self.overwrite_check.isChecked():
                    self.log_message(f"Skipping existing: {name}")
                    continue

                if name.endswith('.ico'):
                    # create multi-size ico
                    ico_sizes = size  # list
                    ico_images = []
                    for s in ico_sizes:
                        if is_svg:
                            # for svg, we'd need cairosvg; fallback: skip ico generation
                            self.log_message("ICO generation from SVG requires cairosvg. Skipping ICO.")
                            break
                        else:
                            resized = img.resize((s, s), Image.Resampling.LANCZOS)
                            ico_images.append(resized)
                    if ico_images:
                        ico_images[0].save(target, format='ICO', sizes=[(s,s) for s in ico_sizes], append_images=ico_images[1:])
                        self.log_message(f"Generated: {name}")

                else:
                    if is_svg:
                        # copy svg as is for png? no, better to convert with cairosvg if needed
                        # for simplicity, we skip png generation from svg (unless you install cairosvg)
                        self.log_message(f"Skipping {name} – SVG source requires cairosvg for raster conversion.")
                        continue
                    else:
                        resized = img.resize((size, size), Image.Resampling.LANCZOS)

                        resized.save(target, 'PNG')
                        self.log_message(f"Generated: {name}")

                self.progress.setValue(self.progress.value() + 1)

            # also copy source svg as favicon.svg if source is svg
            if is_svg and self.generate_svg.isChecked():
                svg_target = output_path / "favicon.svg"
                shutil.copy2(self.source_path, svg_target)
                self.log_message("Copied source SVG as favicon.svg")


            # generate html link tags
            html_links = []
            html_links.append('<link rel="icon" type="image/x-icon" href="favicon.ico">')
            html_links.append('<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">')
            html_links.append('<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">')
            html_links.append('<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">')
            html_links.append('<link rel="manifest" href="site.webmanifest">')  # optional, but good
            # also add android chrome (they use webmanifest usually)
            # for simplicity, we just output a block

            # if html injection requested
            if self.inject_check.isChecked() and self.html_file_label.text():
                html_path = self.html_file_label.text()
                if os.path.isfile(html_path):
                    self.inject_into_html(html_path, html_links, output_path.name + "/")
                    self.log_message(f"Injected favicon links into {html_path}")
                else:
                    self.log_message("HTML file not found, skipping injection.")
            else:
                # just display the links for manual copy
                self.log_message("\n--- Copy these <link> tags into your <head> ---")
                for link in html_links:
                    self.log_message(link)
                self.log_message("Also create a site.webmanifest file if needed.")

            self.log_message("Favicon generation completed.")

            QMessageBox.information(self, "Success", "Favicon generation finished. Check the log for details.")
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            QMessageBox.critical(self, "Error", f"Generation failed: {str(e)}")
        finally:
            self.gen_btn.setEnabled(True)
            self.progress.setVisible(False)

    def inject_into_html(self, html_file, link_tags, icon_folder_rel_path=""):
        from bs4 import BeautifulSoup
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        head = soup.head
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)
        # remove existing favicon links (optional)
        for tag in head.find_all('link', rel=lambda x: x and 'icon' in x):
            tag.decompose()
        for tag in head.find_all('link', rel='apple-touch-icon'):
            tag.decompose()
        # insert new ones (with relative path)
        base_path = icon_folder_rel_path.rstrip('/') + '/' if icon_folder_rel_path else ''
        for link in link_tags:
            # adjust href to include folder if needed
            # for simplicity, we assume the generated icons are in the same folder as html or a subfolder
            # in a real scenario, you'd ask the user for the relative path from html to icons
            # we'll just insert as is – user can edit
            new_tag = soup.new_tag('link', **self.parse_link_tag(link))
            head.append(new_tag)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    @staticmethod
    def parse_link_tag(tag_str):
        """Convert e.g. '<link rel="icon" href="favicon.ico">' to dict."""

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(tag_str, 'html.parser')
        link = soup.find('link')
        if not link:
            return {}
        return {k: v for k, v in link.attrs.items()}
