"""
Aether Security Tab - CSP & SRI Generator
Content Security Policy (CSP) and Subresource Integrity (SRI) for web security
"""

import hashlib
import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QGroupBox, QFormLayout,
    QLineEdit, QApplication, QTabWidget
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class SecurityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.current_csp = None
        self.current_integrity = None
        self.current_sri_url = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File selection
        file_row = QHBoxLayout()
        self.file_label = QLabel("No HTML file selected")
        self.select_btn = QPushButton("\f15c Select HTML File")
        self.select_btn.clicked.connect(self.select_file)
        file_row.addWidget(self.select_btn)
        file_row.addWidget(self.file_label)
        file_row.addStretch()
        layout.addLayout(file_row)

        # Create tab widget for CSP and SRI
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # ========== TAB 1: CSP GENERATOR ==========
        csp_tab = QWidget()
        csp_layout = QVBoxLayout(csp_tab)

        csp_desc = QLabel(
            "\f023 Content Security Policy (CSP) helps prevent XSS attacks by controlling which resources can be loaded.\n"
            "Configure your policy below, then inject into your HTML file."
        )
        csp_desc.setWordWrap(True)
        csp_layout.addWidget(csp_desc)

        # CSP Options
        csp_form = QFormLayout()

        self.csp_default = QLineEdit("'self'")
        csp_form.addRow("default-src:", self.csp_default)

        self.csp_script = QLineEdit("'self' 'unsafe-inline'")
        csp_form.addRow("script-src:", self.csp_script)

        self.csp_style = QLineEdit("'self' 'unsafe-inline'")
        csp_form.addRow("style-src:", self.csp_style)

        self.csp_img = QLineEdit("'self' data: https:")
        csp_form.addRow("img-src:", self.csp_img)

        self.csp_font = QLineEdit("'self' https://fonts.gstatic.com")
        csp_form.addRow("font-src:", self.csp_font)

        self.csp_connect = QLineEdit("'self'")
        csp_form.addRow("connect-src:", self.csp_connect)

        self.csp_frame = QLineEdit("'none'")
        csp_form.addRow("frame-src:", self.csp_frame)

        self.csp_media = QLineEdit("'self'")
        csp_form.addRow("media-src:", self.csp_media)

        self.csp_object = QLineEdit("'none'")
        csp_form.addRow("object-src:", self.csp_object)

        csp_layout.addLayout(csp_form)

        # Preset buttons
        preset_row = QHBoxLayout()
        self.basic_preset = QPushButton("Basic Preset")
        self.basic_preset.clicked.connect(self.load_basic_preset)
        self.strict_preset = QPushButton("Strict Preset")
        self.strict_preset.clicked.connect(self.load_strict_preset)
        self.relaxed_preset = QPushButton("Relaxed Preset")
        self.relaxed_preset.clicked.connect(self.load_relaxed_preset)
        preset_row.addWidget(self.basic_preset)
        preset_row.addWidget(self.strict_preset)
        preset_row.addWidget(self.relaxed_preset)
        csp_layout.addLayout(preset_row)

        # Generate button and preview
        self.generate_csp_btn = QPushButton("\f0ad Generate CSP Meta Tag")
        self.generate_csp_btn.clicked.connect(self.generate_csp)
        csp_layout.addWidget(self.generate_csp_btn)

        self.csp_preview = QPlainTextEdit()
        self.csp_preview.setReadOnly(True)
        self.csp_preview.setMaximumHeight(100)
        self.csp_preview.setPlaceholderText("Generated CSP meta tag will appear here...")
        csp_layout.addWidget(QLabel("Preview:"))
        csp_layout.addWidget(self.csp_preview)

        self.inject_csp_btn = QPushButton("\f055 Inject CSP into HTML")
        self.inject_csp_btn.clicked.connect(self.inject_csp)
        self.inject_csp_btn.setEnabled(False)
        csp_layout.addWidget(self.inject_csp_btn)

        self.tab_widget.addTab(csp_tab, "\f3ed CSP Generator")

        # ========== TAB 2: SRI GENERATOR ==========
        sri_tab = QWidget()
        sri_layout = QVBoxLayout(sri_tab)

        sri_desc = QLabel(
            "\f3c1 Subresource Integrity (SRI) ensures that resources loaded from CDNs haven't been tampered with.\n"
            "Enter a script or style URL to generate its integrity hash."
        )
        sri_desc.setWordWrap(True)
        sri_layout.addWidget(sri_desc)

        # SRI URL input
        url_row = QHBoxLayout()
        self.sri_url = QLineEdit()
        self.sri_url.setPlaceholderText("https://cdn.example.com/script.js or style.css")
        self.sri_url.setMinimumHeight(30)
        url_row.addWidget(self.sri_url)
        self.generate_sri_btn = QPushButton("\f3c1 Generate SRI Hash")
        self.generate_sri_btn.clicked.connect(self.generate_sri)
        url_row.addWidget(self.generate_sri_btn)
        sri_layout.addLayout(url_row)

        # Results display
        self.sri_result = QLabel("Enter a script or style URL and click Generate")
        self.sri_result.setWordWrap(True)
        self.sri_result.setStyleSheet("padding: 10px; font-family: monospace;")
        sri_layout.addWidget(self.sri_result)

        self.inject_sri_btn = QPushButton("💉 Inject SRI into HTML")
        self.inject_sri_btn.clicked.connect(self.inject_sri)
        self.inject_sri_btn.setEnabled(False)
        sri_layout.addWidget(self.inject_sri_btn)

        self.tab_widget.addTab(sri_tab, "\f3c1 SRI Generator")

        # Status bar
        self.status_label = QLabel("Ready - Select an HTML file, then configure CSP or SRI")
        layout.addWidget(self.status_label)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html)")
        if path:
            self.current_file = path
            self.file_label.setText(Path(path).name)
            self.status_label.setText(f"Loaded: {Path(path).name}")

    def load_basic_preset(self):
        self.csp_default.setText("'self'")
        self.csp_script.setText("'self' 'unsafe-inline'")
        self.csp_style.setText("'self' 'unsafe-inline'")
        self.csp_img.setText("'self' data: https:")
        self.csp_font.setText("'self' https://fonts.gstatic.com")
        self.csp_connect.setText("'self'")
        self.csp_frame.setText("'self'")
        self.csp_media.setText("'self'")
        self.csp_object.setText("'none'")
        self.status_label.setText("Basic CSP preset loaded")

    def load_strict_preset(self):
        self.csp_default.setText("'self'")
        self.csp_script.setText("'self'")
        self.csp_style.setText("'self'")
        self.csp_img.setText("'self' data:")
        self.csp_font.setText("'self'")
        self.csp_connect.setText("'self'")
        self.csp_frame.setText("'none'")
        self.csp_media.setText("'self'")
        self.csp_object.setText("'none'")
        self.status_label.setText("Strict CSP preset loaded (highest security)")

    def load_relaxed_preset(self):
        self.csp_default.setText("'self'")
        self.csp_script.setText("'self' 'unsafe-inline' 'unsafe-eval' https:")
        self.csp_style.setText("'self' 'unsafe-inline' https:")
        self.csp_img.setText("* data:")
        self.csp_font.setText("*")
        self.csp_connect.setText("*")
        self.csp_frame.setText("*")
        self.csp_media.setText("*")
        self.csp_object.setText("'self'")
        self.status_label.setText("Relaxed CSP preset loaded (less secure, more compatible)")

    def generate_csp(self):
        policy = f"default-src {self.csp_default.text()}; " \
                 f"script-src {self.csp_script.text()}; " \
                 f"style-src {self.csp_style.text()}; " \
                 f"img-src {self.csp_img.text()}; " \
                 f"font-src {self.csp_font.text()}; " \
                 f"connect-src {self.csp_connect.text()}; " \
                 f"frame-src {self.csp_frame.text()}; " \
                 f"media-src {self.csp_media.text()}; " \
                 f"object-src {self.csp_object.text()};"
        
        meta_tag = f'<meta http-equiv="Content-Security-Policy" content="{policy}">'
        self.csp_preview.setPlainText(meta_tag)
        self.current_csp = policy
        self.inject_csp_btn.setEnabled(True)
        self.status_label.setText("CSP generated. Click 'Inject' to add to HTML.")

    def inject_csp(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Select an HTML file first.")
            return
        if not self.current_csp:
            QMessageBox.warning(self, "Warning", "Generate CSP first.")
            return

        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            head = soup.head
            if not head:
                head = soup.new_tag('head')
                soup.html.insert(0, head)

            # Remove existing CSP
            for meta in soup.find_all('meta', attrs={'http-equiv': 'Content-Security-Policy'}):
                meta.decompose()

            # Add new CSP
            meta = soup.new_tag('meta', **{'http-equiv': 'Content-Security-Policy', 'content': self.current_csp})
            head.append(meta)

            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))

            QMessageBox.information(self, "Success", "CSP injected into HTML file.")
            self.status_label.setText(f"CSP injected into {Path(self.current_file).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to inject CSP: {e}")

    def generate_sri(self):
        url = self.sri_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a script or style URL.")
            return

        self.status_label.setText(f"Fetching {url} to generate SRI hash...")
        QApplication.processEvents()

        try:
            response = requests.get(url, timeout=10, verify=True)
            response.raise_for_status()
            content = response.content
            
            # Generate SHA-384 hash (industry standard)
            hash_sha384 = hashlib.sha384(content).hexdigest()
            integrity = f"sha384-{hash_sha384}"
            
            # Detect if it's a script or style
            if url.endswith('.css'):
                tag_example = f'<link rel="stylesheet" href="{url}" integrity="{integrity}" crossorigin="anonymous">'
            else:
                tag_example = f'<script src="{url}" integrity="{integrity}" crossorigin="anonymous"></script>'
            
            result_text = f"\f00c Integrity hash generated!\n\n"
            result_text += f"Hash: {integrity}\n\n"
            result_text += f"Example usage:\n{tag_example}"
            
            self.sri_result.setText(result_text)
            self.current_integrity = integrity
            self.current_sri_url = url
            self.inject_sri_btn.setEnabled(True)
            self.status_label.setText("SRI hash generated. Click 'Inject' to add to HTML.")
            
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch URL: {e}")
            self.status_label.setText("Failed to generate SRI hash. Check URL and try again.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error: {e}")

    def inject_sri(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Select an HTML file first.")
            return
        if not hasattr(self, 'current_integrity'):
            QMessageBox.warning(self, "Warning", "Generate SRI hash first.")
            return

        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

            found = False
            url_clean = self.current_sri_url.split('/')[-1]  # Get filename
            
            # Find script or link tag with matching src/href
            for script in soup.find_all('script', src=True):
                if url_clean in script['src'] or self.current_sri_url in script['src']:
                    script['integrity'] = self.current_integrity
                    script['crossorigin'] = 'anonymous'
                    found = True
                    self.status_label.setText(f"Added SRI to: {script['src']}")
            
            for link in soup.find_all('link', rel='stylesheet', href=True):
                if url_clean in link['href'] or self.current_sri_url in link['href']:
                    link['integrity'] = self.current_integrity
                    link['crossorigin'] = 'anonymous'
                    found = True
                    self.status_label.setText(f"Added SRI to: {link['href']}")

            if not found:
                reply = QMessageBox.question(self, "Not Found", 
                    f"Could not find a tag with '{url_clean}' or '{self.current_sri_url}' in your HTML.\n\n"
                    f"Add it manually using the example above.\n\n"
                    f"Continue without saving?",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return

            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))

            if found:
                QMessageBox.information(self, "Success", "SRI attributes added to tag(s).")
            self.status_label.setText(f"SRI processed for {Path(self.current_file).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to inject SRI: {e}")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.csp_preview.setStyleSheet("background-color: #2B2D31; color: #E8E8E8;")
            self.sri_result.setStyleSheet("padding: 10px; font-family: monospace; background-color: #2B2D31; color: #E8E8E8;")
        else:
            self.csp_preview.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")
            self.sri_result.setStyleSheet("padding: 10px; font-family: monospace; background-color: #FFFFFF; color: #2C3E50;")
