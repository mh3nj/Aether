import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QGroupBox, QFormLayout,
    QLineEdit, QCheckBox, QScrollArea, QProgressBar, QApplication
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class OGPreviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.project_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # mode selection
        mode_row = QHBoxLayout()
        self.single_mode_btn = QPushButton("\uf15c Single File Mode")
        self.single_mode_btn.setCheckable(True)
        self.single_mode_btn.setChecked(True)
        self.single_mode_btn.clicked.connect(lambda: self.set_mode("single"))
        self.bulk_mode_btn = QPushButton("\uf07c Bulk Mode (Folder)")
        self.bulk_mode_btn.setCheckable(True)
        self.bulk_mode_btn.clicked.connect(lambda: self.set_mode("bulk"))
        mode_row.addWidget(self.single_mode_btn)
        mode_row.addWidget(self.bulk_mode_btn)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        # single file selection
        self.single_widget = QWidget()
        single_layout = QHBoxLayout(self.single_widget)
        self.file_label = QLabel("No HTML file selected")
        self.select_btn = QPushButton("Select HTML File")
        self.select_btn.clicked.connect(self.select_html_file)

        single_layout.addWidget(self.select_btn)
        single_layout.addWidget(self.file_label)
        single_layout.addStretch()
        layout.addWidget(self.single_widget)

        # bulk folder selection
        self.bulk_widget = QWidget()
        bulk_layout = QHBoxLayout(self.bulk_widget)
        self.folder_label = QLabel("No folder selected")
        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        bulk_layout.addWidget(self.select_folder_btn)
        bulk_layout.addWidget(self.folder_label)
        bulk_layout.addStretch()
        self.bulk_widget.setVisible(False)
        layout.addWidget(self.bulk_widget)


        # edit fields
        edit_group = QGroupBox("Open Graph & Twitter Card Tags")
        edit_layout = QFormLayout(edit_group)
        
        # og tags
        self.og_title = QLineEdit()
        self.og_title.setPlaceholderText("Open Graph Title")
        edit_layout.addRow("OG Title:", self.og_title)
        self.og_desc = QLineEdit()
        self.og_desc.setPlaceholderText("Open Graph Description")
        edit_layout.addRow("OG Description:", self.og_desc)
        self.og_image = QLineEdit()
        self.og_image.setPlaceholderText("https://example.com/image.jpg")
        edit_layout.addRow("OG Image URL:", self.og_image)
        self.og_url = QLineEdit()
        self.og_url.setPlaceholderText("https://example.com/page.html")
        edit_layout.addRow("OG URL:", self.og_url)
        self.og_type = QLineEdit()
        self.og_type.setPlaceholderText("website, article, product, etc.")
        edit_layout.addRow("OG Type:", self.og_type)
        self.og_locale = QLineEdit()
        self.og_locale.setPlaceholderText("en_US, fa_IR, etc.")
        edit_layout.addRow("OG Locale:", self.og_locale)
        
        # twitter tags
        self.tw_title = QLineEdit()
        self.tw_title.setPlaceholderText("Twitter Card Title")
        edit_layout.addRow("Twitter Title:", self.tw_title)
        self.tw_desc = QLineEdit()
        self.tw_desc.setPlaceholderText("Twitter Card Description")
        edit_layout.addRow("Twitter Description:", self.tw_desc)
        self.tw_image = QLineEdit()
        self.tw_image.setPlaceholderText("https://example.com/image.jpg")
        edit_layout.addRow("Twitter Image:", self.tw_image)
        self.tw_card = QLineEdit()
        self.tw_card.setPlaceholderText("summary, summary_large_image, app, player")
        edit_layout.addRow("Twitter Card Type:", self.tw_card)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)

        # preview and injection buttons
        btn_row = QHBoxLayout()
        self.preview_btn = QPushButton("\uf06e Generate Preview")
        self.preview_btn.clicked.connect(self.generate_preview)
        self.inject_btn = QPushButton("\uf055 Inject Tags into HTML")

        self.inject_btn.clicked.connect(self.inject_tags)
        self.bulk_inject_btn = QPushButton("\uf187 Bulk Inject into All HTML Files")
        self.bulk_inject_btn.clicked.connect(self.bulk_inject_tags)

        btn_row.addWidget(self.preview_btn)
        btn_row.addWidget(self.inject_btn)
        btn_row.addWidget(self.bulk_inject_btn)
        layout.addLayout(btn_row)

        # progress bar for bulk operations
        self.progress = QProgressBar()

        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # preview area
        preview_group = QGroupBox("Social Media Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.fb_preview = QLabel()
        self.fb_preview.setWordWrap(True)
        self.fb_preview.setAlignment(Qt.AlignTop)
        preview_layout.addWidget(QLabel("\uf02d Facebook / LinkedIn / WhatsApp:"))
        preview_layout.addWidget(self.fb_preview)
        
        self.tw_preview = QLabel()
        self.tw_preview.setWordWrap(True)
        self.tw_preview.setAlignment(Qt.AlignTop)
        preview_layout.addWidget(QLabel("\uf099 Twitter / X:"))
        preview_layout.addWidget(self.tw_preview)
        
        layout.addWidget(preview_group)


        # raw tags display  # i have no idea what this does
        raw_group = QGroupBox("Current / Extracted Meta Tags")
        raw_layout = QVBoxLayout(raw_group)
        self.raw_tags = QPlainTextEdit()
        self.raw_tags.setReadOnly(True)
        self.raw_tags.setMaximumHeight(120)
        raw_layout.addWidget(self.raw_tags)
        layout.addWidget(raw_group)

        self.status_label = QLabel("Ready - Select file/folder, edit tags, then Inject or Generate Preview")
        layout.addWidget(self.status_label)

        self.current_mode = "single"


    def set_mode(self, mode):
        self.current_mode = mode
        if mode == "single":
            self.single_mode_btn.setChecked(True)
            self.bulk_mode_btn.setChecked(False)
            self.single_widget.setVisible(True)
            self.bulk_widget.setVisible(False)

            self.bulk_inject_btn.setEnabled(False)
            self.inject_btn.setEnabled(True)
        else:
            self.single_mode_btn.setChecked(False)
            self.bulk_mode_btn.setChecked(True)
            self.single_widget.setVisible(False)
            self.bulk_widget.setVisible(True)
            self.bulk_inject_btn.setEnabled(True)
            self.inject_btn.setEnabled(False)

    def select_html_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html)")
        if path:
            self.current_file = path
            self.file_label.setText(Path(path).name)
            self.load_existing_tags(path)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder with HTML Files")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def load_existing_tags(self, file_path):
        """Load existing OG/Twitter tags from HTML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        self.og_title.setText(self.get_meta_content(soup, 'og:title') or "")
        self.og_desc.setText(self.get_meta_content(soup, 'og:description') or "")
        self.og_image.setText(self.get_meta_content(soup, 'og:image') or "")
        self.og_url.setText(self.get_meta_content(soup, 'og:url') or "")
        self.og_type.setText(self.get_meta_content(soup, 'og:type') or "")
        self.og_locale.setText(self.get_meta_content(soup, 'og:locale') or "")
        self.tw_title.setText(self.get_meta_content(soup, 'twitter:title') or "")
        self.tw_desc.setText(self.get_meta_content(soup, 'twitter:description') or "")
        self.tw_image.setText(self.get_meta_content(soup, 'twitter:image') or "")
        self.tw_card.setText(self.get_meta_content(soup, 'twitter:card') or "")

    def get_meta_content(self, soup, property_name):
        """Extract meta tag content by property or name."""
        meta = soup.find('meta', attrs={'property': property_name})
        if meta and meta.get('content'):
            return meta['content']
        meta = soup.find('meta', attrs={'name': property_name})
        if meta and meta.get('content'):
            return meta['content']
        return None

    def generate_preview(self):
        if self.current_mode == "single" and not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select an HTML file first.")
            return

        # use current field values (with overrides)
        og_title = self.og_title.text().strip() or "No Title"

        og_desc = self.og_desc.text().strip() or "No description provided"
        og_image = self.og_image.text().strip() or "https://via.placeholder.com/1200x630"
        og_url = self.og_url.text().strip() or "https://example.com"
        og_type = self.og_type.text().strip() or "website"
        twitter_title = self.tw_title.text().strip() or og_title

        twitter_desc = self.tw_desc.text().strip() or og_desc
        twitter_image = self.tw_image.text().strip() or og_image
        twitter_card = self.tw_card.text().strip() or "summary_large_image"

        # build facebook preview
        fb_html = f"""
        <div style="max-width: 500px; font-family: Helvetica, Arial, sans-serif;">
            <div style="background-color: #f0f2f5; border-radius: 8px; overflow: hidden;">
                <img src="{og_image}" style="width: 100%; max-height: 260px; object-fit: cover;" 
                     onerror="this.src='https://via.placeholder.com/500x260?text=No+Image'">
                <div style="padding: 12px;">
                    <div style="font-size: 12px; color: #606770; text-transform: uppercase; margin-bottom: 4px;">{og_url}</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1b1f23; margin-bottom: 4px;">{og_title[:100]}</div>  # works on my machine
                    <div style="font-size: 14px; color: #606770; line-height: 1.4;">{og_desc[:200]}</div>

                </div>
            </div>
        </div>
        """
        
        # build twitter preview
        tw_html = f"""
        <div style="max-width: 500px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e1e8ed;">
                <img src="{twitter_image}" style="width: 100%; max-height: 260px; object-fit: cover;"
                     onerror="this.src='https://via.placeholder.com/500x260?text=No+Image'">
                <div style="padding: 12px;">
                    <div style="font-size: 15px; font-weight: 700; color: #0f1419; margin-bottom: 4px;">{twitter_title[:100]}</div>
                    <div style="font-size: 14px; color: #536471; line-height: 1.4;">{twitter_desc[:200]}</div>
                    <div style="font-size: 13px; color: #536471; margin-top: 8px;">\uf140 {twitter_card}</div>
                </div>
            </div>
        </div>
        """

        self.fb_preview.setText(fb_html)
        self.tw_preview.setText(tw_html)
        
        # show raw tags
        raw_text = f"""Open Graph:
  og:title = {og_title}
  og:description = {og_desc}
  og:image = {og_image}
  og:url = {og_url}
  og:type = {og_type}
  og:locale = {self.og_locale.text().strip() or '(not set)'}

Twitter Card:
  twitter:title = {twitter_title}
  twitter:description = {twitter_desc}
  twitter:image = {twitter_image}
  twitter:card = {twitter_card}
"""
        self.raw_tags.setPlainText(raw_text)
        self.status_label.setText("Preview generated")

    def inject_tags(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select an HTML file first.")
            return

        self._inject_into_file(self.current_file)
        QMessageBox.information(self, "Success", f"OG/Twitter tags injected into {Path(self.current_file).name}")

    def bulk_inject_tags(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            QMessageBox.warning(self, "Warning", "No HTML files found in the selected folder.")
            return

        reply = QMessageBox.question(self, "Confirm Bulk Inject", 
                                     f"Inject OG/Twitter tags into {len(html_files)} HTML files?\nThis will add/replace tags in all files.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.bulk_inject_btn.setEnabled(False)
        
        success_count = 0
        for idx, html_path in enumerate(html_files):
            try:
                self._inject_into_file(str(html_path))
                success_count += 1
            except Exception as e:
                self.status_label.setText(f"Error: {html_path.name} - {str(e)[:50]}")
            self.progress.setValue(idx + 1)
            QApplication.processEvents()
        
        self.progress.setVisible(False)
        self.bulk_inject_btn.setEnabled(True)
        QMessageBox.information(self, "Bulk Inject Complete", 

                                f"Injected tags into {success_count} of {len(html_files)} files.")
        self.status_label.setText(f"Bulk inject completed: {success_count} files updated")

    def _inject_into_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        head = soup.head
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)
        
        # remove existing og/twitter tags
        meta_properties = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type', 'og:locale']
        meta_names = ['twitter:title', 'twitter:description', 'twitter:image', 'twitter:card']
        
        for prop in meta_properties:
            existing = soup.find('meta', attrs={'property': prop})
            if existing:
                existing.decompose()
        
        for name in meta_names:
            existing = soup.find('meta', attrs={'name': name})
            if existing:
                existing.decompose()
        
        # insert new og tags
        if self.og_title.text().strip():
            tag = soup.new_tag('meta')
            tag['property'] = 'og:title'
            tag['content'] = self.og_title.text().strip()
            head.append(tag)
        
        if self.og_desc.text().strip():
            tag = soup.new_tag('meta')
            tag['property'] = 'og:description'
            tag['content'] = self.og_desc.text().strip()
            head.append(tag)
        
        if self.og_image.text().strip():
            tag = soup.new_tag('meta')
            tag['property'] = 'og:image'
            tag['content'] = self.og_image.text().strip()
            head.append(tag)
        
        if self.og_url.text().strip():
            tag = soup.new_tag('meta')
            tag['property'] = 'og:url'
            tag['content'] = self.og_url.text().strip()
            head.append(tag)
        
        if self.og_type.text().strip():
            tag = soup.new_tag('meta')
            tag['property'] = 'og:type'
            tag['content'] = self.og_type.text().strip()
            head.append(tag)
        
        if self.og_locale.text().strip():
            tag = soup.new_tag('meta')
            tag['property'] = 'og:locale'
            tag['content'] = self.og_locale.text().strip()
            head.append(tag)
        
        # insert new twitter tags
        if self.tw_title.text().strip():
            tag = soup.new_tag('meta')
            tag['name'] = 'twitter:title'
            tag['content'] = self.tw_title.text().strip()
            head.append(tag)
        
        if self.tw_desc.text().strip():
            tag = soup.new_tag('meta')
            tag['name'] = 'twitter:description'
            tag['content'] = self.tw_desc.text().strip()
            head.append(tag)

        
        if self.tw_image.text().strip():
            tag = soup.new_tag('meta')
            tag['name'] = 'twitter:image'
            tag['content'] = self.tw_image.text().strip()
            head.append(tag)
        
        if self.tw_card.text().strip():

            tag = soup.new_tag('meta')
            tag['name'] = 'twitter:card'
            tag['content'] = self.tw_card.text().strip()
            head.append(tag)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.fb_preview.setStyleSheet("""
                QLabel {
                    background-color: #1e1f22;
                    border: 1px solid #3e4045;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            self.tw_preview.setStyleSheet("""
                QLabel {
                    background-color: #1e1f22;
                    border: 1px solid #3e4045;
                    border-radius: 16px;
                    padding: 12px;
                }
            """)
        else:
            self.fb_preview.setStyleSheet("""
                QLabel {
                    background-color: #f0f2f5;
                    border: 1px solid #d0d7de;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
            self.tw_preview.setStyleSheet("""
                QLabel {
                    background-color: #ffffff;
                    border: 1px solid #e1e8ed;
                    border-radius: 16px;
                    padding: 12px;
                }
            """)
