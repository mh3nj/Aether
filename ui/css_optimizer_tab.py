import os
import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QFormLayout, QLineEdit, QCheckBox, QComboBox, QApplication
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class CSSOptimizerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_css_file = None
        self.current_html_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # CSS file selection
        css_row = QHBoxLayout()
        self.css_label = QLabel("No CSS file selected")
        self.select_css_btn = QPushButton("Select Main CSS File")
        self.select_css_btn.clicked.connect(self.select_css_file)
        css_row.addWidget(self.select_css_btn)
        css_row.addWidget(self.css_label)
        css_row.addStretch()
        layout.addLayout(css_row)

        # HTML folder selection (optional)
        html_row = QHBoxLayout()
        self.html_label = QLabel("No HTML folder selected (optional)")
        self.select_html_btn = QPushButton("Select HTML Folder")
        self.select_html_btn.clicked.connect(self.select_html_folder)
        html_row.addWidget(self.select_html_btn)
        html_row.addWidget(self.html_label)
        html_row.addStretch()
        layout.addLayout(html_row)

        # Generation options
        opts_group = QGroupBox("Generation Options")
        opts_layout = QFormLayout()

        self.output_method = QComboBox()
        self.output_method.addItems(["Embed in existing CSS file", "Create separate print.css", "Create separate print.css + speech.css"])
        opts_layout.addRow("Output method:", self.output_method)

        self.remove_nav = QCheckBox("Hide navigation menus, sidebars, footers when printing")
        self.remove_nav.setChecked(True)
        opts_layout.addRow(self.remove_nav)

        self.remove_ads = QCheckBox("Hide advertisement sections")
        self.remove_ads.setChecked(True)
        opts_layout.addRow(self.remove_ads)

        self.remove_bg = QCheckBox("Remove background colors/images for printing (saves ink)")
        self.remove_bg.setChecked(True)
        opts_layout.addRow(self.remove_bg)

        self.black_white = QCheckBox("Convert all text to black/dark gray for printing")
        self.black_white.setChecked(True)
        opts_layout.addRow(self.black_white)

        self.add_page_breaks = QCheckBox("Add page breaks before major sections")
        self.add_page_breaks.setChecked(False)
        opts_layout.addRow(self.add_page_breaks)

        self.include_links = QCheckBox("Show link URLs in parentheses when printing")
        self.include_links.setChecked(True)
        opts_layout.addRow(self.include_links)

        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Preview area
        preview_group = QGroupBox("Generated CSS Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMaximumHeight(300)
        preview_layout.addWidget(self.preview)
        layout.addWidget(preview_group)

        # Buttons
        btn_row = QHBoxLayout()
        self.generate_btn = QPushButton("🔧 Generate Print/Speech CSS")
        self.generate_btn.clicked.connect(self.generate_css)
        self.inject_btn = QPushButton("💉 Inject into HTML Files")
        self.inject_btn.clicked.connect(self.inject_into_html)
        btn_row.addWidget(self.generate_btn)
        btn_row.addWidget(self.inject_btn)
        layout.addLayout(btn_row)

        self.status_label = QLabel("Ready - Select a CSS file and click Generate")
        layout.addWidget(self.status_label)

    def select_css_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSS File", "", "CSS Files (*.css)")
        if path:
            self.current_css_file = path
            self.css_label.setText(Path(path).name)
            self.load_css_preview()

    def select_html_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select HTML Project Folder")
        if path:
            self.current_html_folder = path
            self.html_label.setText(path)

    def load_css_preview(self):
        with open(self.current_css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.preview.setPlainText(content[:500] + "\n...\n[Preview of existing CSS]")

    def generate_css(self):
        if not self.current_css_file:
            QMessageBox.warning(self, "Warning", "Please select a CSS file first.")
            return

        # Generate print CSS
        print_css = self.generate_print_css()
        speech_css = self.generate_speech_css()

        combined_preview = "/* ========================================== */\n"
        combined_preview += "/* PRINT MEDIA QUERY - Optimized for printing */\n"
        combined_preview += "/* ========================================== */\n\n"
        combined_preview += print_css
        combined_preview += "\n\n/* ========================================== */\n"
        combined_preview += "/* SPEECH MEDIA QUERY - For screen readers */\n"
        combined_preview += "/* ========================================== */\n\n"
        combined_preview += speech_css

        self.preview.setPlainText(combined_preview)

        # Save based on output method
        method = self.output_method.currentText()
        
        if "Embed" in method:
            # Append to existing CSS file
            with open(self.current_css_file, 'a', encoding='utf-8') as f:
                f.write("\n\n" + combined_preview)
            QMessageBox.information(self, "Success", f"Print/speech CSS appended to {Path(self.current_css_file).name}")
        elif "separate print.css" in method:
            output_path = Path(self.current_css_file).parent / "print.css"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(print_css)
            self.status_label.setText(f"Created: {output_path}")
            QMessageBox.information(self, "Success", f"Created print.css\nSave location: {output_path}")
        else:
            # Create both
            print_path = Path(self.current_css_file).parent / "print.css"
            speech_path = Path(self.current_css_file).parent / "speech.css"
            with open(print_path, 'w', encoding='utf-8') as f:
                f.write(print_css)
            with open(speech_path, 'w', encoding='utf-8') as f:
                f.write(speech_css)
            self.status_label.setText(f"Created: print.css and speech.css")
            QMessageBox.information(self, "Success", f"Created:\n- print.css\n- speech.css\n\nLocation: {Path(self.current_css_file).parent}")

    def generate_print_css(self):
        """Generate optimal CSS for printing"""
        css = "@media print {\n"
        css += "    /* Hide non-essential elements for printing */\n"
        
        if self.remove_nav.isChecked():
            css += "    nav, header, footer, aside, .sidebar, .navigation, .menu, .comments, .social-share {\n"
            css += "        display: none !important;\n"
            css += "    }\n\n"
        
        if self.remove_ads.isChecked():
            css += "    .ad, .advertisement, .promo, .banner, [class*='ad-'], [class*='ads'] {\n"
            css += "        display: none !important;\n"
            css += "    }\n\n"
        
        if self.remove_bg.isChecked():
            css += "    /* Remove backgrounds to save ink */\n"
            css += "    body, div, section, article, main {\n"
            css += "        background-color: white !important;\n"
            css += "        background-image: none !important;\n"
            css += "    }\n\n"
        
        if self.black_white.isChecked():
            css += "    /* Ensure text is readable and ink-friendly */\n"
            css += "    body, p, h1, h2, h3, h4, h5, h6, li, span, div {\n"
            css += "        color: black !important;\n"
            css += "    }\n\n"
        
        if self.include_links.isChecked():
            css += "    /* Show link URLs in parentheses */\n"
            css += "    a[href]:after {\n"
            css += "        content: ' (' attr(href) ')';\n"
            css += "        font-size: 90%;\n"
            css += "    }\n"
            css += "    /* Don't show for internal anchors */\n"
            css += "    a[href^='#']:after {\n"
            css += "        content: '';\n"
            css += "    }\n\n"
        
        if self.add_page_breaks.isChecked():
            css += "    /* Add page breaks for better readability */\n"
            css += "    h1, h2, h3, section, article {\n"
            css += "        page-break-after: avoid;\n"
            css += "        page-break-inside: avoid;\n"
            css += "    }\n\n"
        
        css += "    /* Improve margins for printing */\n"
        css += "    body {\n"
        css += "        margin: 1.5cm;\n"
        css += "        font-size: 12pt;\n"
        css += "        line-height: 1.4;\n"
        css += "    }\n"
        css += "}\n"
        
        return css

    def generate_speech_css(self):
        """Generate CSS optimized for screen readers (speech media type)"""
        css = "@media speech {\n"
        css += "    /* Optimize for screen readers - WCAG compliance */\n"
        css += "    body {\n"
        css += "        voice-family: female;\n"
        css += "        voice-volume: medium;\n"
        css += "        voice-rate: normal;\n"
        css += "        voice-pitch: medium;\n"
        css += "        voice-stress: normal;\n"
        css += "    }\n\n"
        
        css += "    /* Ensure proper pronunciation of special elements */\n"
        css += "    abbr[title]:after {\n"
        css += "        content: ' (' attr(title) ')';\n"
        css += "    }\n\n"
        
        css += "    /* Pause slightly after headings for better comprehension */\n"
        css += "    h1, h2, h3, h4, h5, h6 {\n"
        css += "        pause-after: 200ms;\n"
        css += "        voice-stress: strong;\n"
        css += "    }\n\n"
        
        css += "    /* Add pause after paragraphs */\n"
        css += "    p {\n"
        css += "        pause-after: 100ms;\n"
        css += "    }\n\n"
        
        css += "    /* Skip navigation elements during speech (indicate they exist) */\n"
        css += "    nav:before {\n"
        css += "        content: 'Navigation menu. ';\n"
        css += "    }\n"
        css += "    nav {\n"
        css += "        speak: spell-out;\n"
        css += "    }\n\n"
        
        css += "    /* Handle image alt text properly */\n"
        css += "    img:after {\n"
        css += "        content: ' Image: ' attr(alt);\n"
        css += "    }\n\n"
        
        css += "    /* Make links clear */\n"
        css += "    a[href]:before {\n"
        css += "        content: 'Link to ';\n"
        css += "    }\n"
        css += "    a[href]:after {\n"
        css += "        content: ', ';\n"
        css += "    }\n"
        css += "}\n"
        
        return css

    def inject_into_html(self):
        """Add semantic HTML structure and link CSS files to HTML pages"""
        if not self.current_html_folder:
            QMessageBox.warning(self, "Warning", "Please select an HTML folder first.")
            return

        html_files = list(Path(self.current_html_folder).rglob("*.html"))
        if not html_files:
            QMessageBox.warning(self, "Warning", "No HTML files found in the selected folder.")
            return

        reply = QMessageBox.question(self, "Inject into HTML",
                                     f"Add semantic HTML structure and link CSS to {len(html_files)} HTML files?\n\n"
                                     f"This will:\n"
                                     f"1. Add/update <link> tags for print.css/speech.css\n"
                                     f"2. Ensure proper <article>/<main> structure for Reader Mode\n"
                                     f"This is safe and won't delete existing content.",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply != QMessageBox.Yes:
            return

        updated = 0
        css_dir = Path(self.current_css_file).parent if self.current_css_file else Path(self.current_html_folder)

        for html_path in html_files:
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                head = soup.head
                if not head:
                    head = soup.new_tag('head')
                    soup.html.insert(0, head)

                # Add print.css if it exists
                print_css_path = css_dir / "print.css"
                if print_css_path.exists():
                    # Remove existing print.css link
                    for link in head.find_all('link', media='print'):
                        link.decompose()
                    # Add new
                    link = soup.new_tag('link', rel='stylesheet', type='text/css', href='print.css', media='print')
                    head.append(link)

                # Add speech.css if it exists
                speech_css_path = css_dir / "speech.css"
                if speech_css_path.exists():
                    for link in head.find_all('link', media='speech'):
                        link.decompose()
                    link = soup.new_tag('link', rel='stylesheet', type='text/css', href='speech.css', media='speech')
                    head.append(link)

                # Ensure semantic HTML structure for Reader Mode
                body = soup.body
                if body:
                    # Wrap main content in <main> if not present
                    if not body.find('main'):
                        # Try to find the main content div
                        main_content = body.find('div', class_=re.compile(r'content|main|article'))
                        if main_content:
                            main_content.name = 'main'
                        else:
                            # Create <main> wrapper around the main text
                            main_tag = soup.new_tag('main')
                            first_div = body.find('div')
                            if first_div:
                                first_div.wrap(main_tag)
                            else:
                                body.insert(0, main_tag)

                    # Ensure article tags for blog content
                    for article_class in ['post', 'article', 'entry']:
                        for div in body.find_all('div', class_=re.compile(article_class)):
                            div.name = 'article'

                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                updated += 1

            except Exception as e:
                self.status_label.setText(f"Error: {html_path.name} - {str(e)[:50]}")

        QMessageBox.information(self, "Injection Complete",
                                f"Updated {updated} of {len(html_files)} HTML files.\n\n"
                                f"Added:\n"
                                f"• <link media='print'> tags\n"
                                f"• <link media='speech'> tags\n"
                                f"• Semantic <main>/<article> structure for Reader Mode")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.setStyleSheet("""
                QGroupBox {
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    color: #E8E8E8;
                }
                QCheckBox {
                    color: #E8E8E8;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QLabel {
                    color: #E8E8E8;
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
            """)
        else:
            self.setStyleSheet("""
                QGroupBox {
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                    margin-top: 10px;
                }
                QGroupBox::title {
                    color: #2C3E50;
                }
                QCheckBox {
                    color: #2C3E50;
                    spacing: 8px;
                }
                QLabel {
                    color: #2C3E50;
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
            """)
