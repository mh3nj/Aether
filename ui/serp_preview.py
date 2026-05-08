"""
Aether SERP Preview Simulator - See how your page looks in Google search results
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QLineEdit, QTextEdit, QGroupBox, QMessageBox, QApplication
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class SERPPreviewTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # File selection
        file_row = QHBoxLayout()
        self.file_label = QLabel("No HTML file selected")
        self.select_btn = QPushButton("Select HTML File")
        self.select_btn.clicked.connect(self.select_file)
        self.preview_btn = QPushButton("Generate SERP Preview")
        self.preview_btn.clicked.connect(self.generate_preview)
        file_row.addWidget(self.select_btn)
        file_row.addWidget(self.preview_btn)
        file_row.addWidget(self.file_label)
        file_row.addStretch()
        layout.addLayout(file_row)

        # Override fields
        edit_group = QGroupBox("Override (optional)")
        edit_layout = QVBoxLayout(edit_group)
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Title (50-60 chars)")
        edit_layout.addWidget(self.title_edit)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com/page.html")
        edit_layout.addWidget(self.url_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("Meta description (150-160 chars)")
        edit_layout.addWidget(self.desc_edit)
        
        layout.addWidget(edit_group)

        # SERP Preview
        preview_group = QGroupBox("Google Search Result Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview = QLabel()
        self.preview.setWordWrap(True)
        self.preview.setAlignment(Qt.AlignTop)
        self.preview.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
                border-radius: 8px;
                padding: 16px;
                font-family: Arial, sans-serif;
            }
        """)
        preview_layout.addWidget(self.preview)
        layout.addWidget(preview_group)

        self.status_label = QLabel("Ready - Select an HTML file")
        layout.addWidget(self.status_label)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html)")
        if path:
            self.current_file = path
            self.file_label.setText(path.split('/')[-1])
            self.load_from_file(path)

    def load_from_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        title = soup.find('title')
        if title:
            self.title_edit.setText(title.string or "")
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            self.desc_edit.setPlainText(meta_desc.get('content', ""))
        
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            self.url_edit.setText(canonical.get('href', ""))
        else:
            self.url_edit.setText(f"https://example.com/{self.file_label.text()}")

    def generate_preview(self):
        title = self.title_edit.text() or "Untitled Page"
        url = self.url_edit.text() or "https://example.com"
        desc = self.desc_edit.toPlainText() or "No description provided"
        
        # Truncate if too long
        if len(title) > 60:
            title = title[:57] + "..."
        if len(desc) > 160:
            desc = desc[:157] + "..."
        
        # Format URL for display
        display_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
        if len(display_url) > 60:
            display_url = display_url[:57] + "..."
        
        # Create SERP preview HTML
        preview_html = f"""
        <div style="max-width: 600px; font-family: Arial, sans-serif;">
            <div style="font-size: 14px; color: #202124; margin-bottom: 2px;">{display_url}</div>
            <div style="font-size: 20px; color: #1A0DAB; margin: 4px 0; text-decoration: underline; cursor: pointer;">
                {title}
            </div>
            <div style="font-size: 14px; color: #4D5156; line-height: 1.4;">{desc}</div>
            <div style="font-size: 12px; color: #70757A; margin-top: 8px;">\uf005 Google SERP Preview — Aether Tool</div>
        </div>
        """
        
        self.preview.setText(preview_html)
        
        # Show character warnings
        warnings = []
        if len(self.title_edit.text()) > 60:
            warnings.append(f"\uf071 Title too long: {len(self.title_edit.text())} chars (max 60)")
        elif len(self.title_edit.text()) < 50:
            warnings.append(f"\uf071 Title too short: {len(self.title_edit.text())} chars (recommend 50-60)")
        
        if len(self.desc_edit.toPlainText()) > 160:
            warnings.append(f"\uf071 Description too long: {len(self.desc_edit.toPlainText())} chars (max 160)")
        elif len(self.desc_edit.toPlainText()) < 120:
            warnings.append(f"\uf071 Description too short: {len(self.desc_edit.toPlainText())} chars (recommend 150-160)")
        
        if warnings:
            self.status_label.setText(" | ".join(warnings))
        else:
            self.status_label.setText("\uf00c Perfect! Title and description are optimally sized")

    def update_theme(self, is_dark):
        if is_dark:
            self.preview.setStyleSheet("""
                QLabel {
                    background-color: #2B2D31;
                    border: 1px solid #3E4045;
                    border-radius: 8px;
                    padding: 16px;
                    font-family: Arial, sans-serif;
                }
            """)
        else:
            self.preview.setStyleSheet("""
                QLabel {
                    background-color: #FFFFFF;
                    border: 1px solid #D0D7DE;
                    border-radius: 8px;
                    padding: 16px;
                    font-family: Arial, sans-serif;
                }
            """)
