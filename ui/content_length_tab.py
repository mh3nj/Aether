"""
Aether Content Length Checker - Ensure pages have enough content for SEO
"""

import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class ContentLengthTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Analyze Content Length")
        self.scan_btn.clicked.connect(self.analyze_content)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Options
        opts_row = QHBoxLayout()
        self.content_type = QComboBox()
        self.content_type.addItems(["All Text", "Main Content Only (article/main)", "Body Text Only"])
        opts_row.addWidget(QLabel("Analyze:"))
        opts_row.addWidget(self.content_type)
        opts_row.addStretch()
        layout.addLayout(opts_row)

        # Quick stats panel
        stats_row = QHBoxLayout()
        self.total_pages_label = QLabel("Total pages: 0")
        self.avg_length_label = QLabel("Avg length: 0 words")
        self.short_pages_label = QLabel("Short pages: 0")
        stats_row.addWidget(self.total_pages_label)
        stats_row.addWidget(self.avg_length_label)
        stats_row.addWidget(self.short_pages_label)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        # Results tree - FIXED: This is where individual pages should appear
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Page", "Word Count", "Status", "Recommendation"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Length guidelines - FIXED: dynamic styling for dark mode
        self.guidelines = QLabel(
            "📏 Content Length Guidelines:\n"
            "• < 300 words: ⚠️ Very short - unlikely to rank\n"
            "• 300-500 words: 🔸 Short - consider expanding\n"
            "• 500-1000 words: ✅ Good - standard for many topics\n"
            "• 1000-2000 words: 🌟 Great - comprehensive content\n"
            "• > 2000 words: 🏆 Excellent - in-depth coverage"
        )
        self.guidelines.setWordWrap(True)
        self.guidelines.setStyleSheet("padding: 8px; border-radius: 4px; margin-top: 5px;")
        layout.addWidget(self.guidelines)

        self.summary_label = QLabel("Ready - Select a folder and click Analyze")
        layout.addWidget(self.summary_label)

        # Store results for later use
        self.analysis_results = []

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def extract_text(self, soup, mode):
        """Extract text based on selected mode"""
        # Remove script and style tags always
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        if mode == "Main Content Only (article/main)":
            # Try to find main content areas
            main_content = soup.find('main')
            if not main_content:
                main_content = soup.find('article')
            if not main_content:
                main_content = soup.find('div', class_=re.compile(r'content|main|article|post|entry'))
            if main_content:
                text = main_content.get_text()
            else:
                # Fallback to body
                text = soup.body.get_text() if soup.body else ""
        elif mode == "Body Text Only":
            # Only body text, exclude headers/footers
            body = soup.body
            if body:
                # Remove common non-content elements
                for tag in body.find_all(['nav', 'header', 'footer', 'aside']):
                    tag.decompose()
                text = body.get_text()
            else:
                text = ""
        else:
            # All text
            text = soup.get_text()
        
        # Clean text - split into words
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def analyze_content(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.summary_label.setText("No HTML files found.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_tree.clear()
        self.analysis_results = []

        mode = self.content_type.currentText()
        total_words = 0
        short_count = 0

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                text = self.extract_text(soup, mode)
                words = text.split()
                word_count = len(words)
                total_words += word_count
                
                rel_path = str(html_path.relative_to(self.project_folder))
                
                # Determine status based on word count
                if word_count < 300:
                    status = "⚠️ Very Short"
                    recommendation = "Add more detailed content (target: 500+ words)"
                    short_count += 1
                elif word_count < 500:
                    status = "🔸 Short"
                    recommendation = "Expand content to 500-1000 words for better ranking"
                    short_count += 1
                elif word_count < 1000:
                    status = "✅ Good"
                    recommendation = "Good length! Consider adding more depth if competitive topic"
                elif word_count < 2000:
                    status = "🌟 Great"
                    recommendation = "Excellent length! This page has strong potential"
                else:
                    status = "🏆 Excellent"
                    recommendation = "Outstanding! Very comprehensive content"
                
                # Create tree item for each page
                item = QTreeWidgetItem([rel_path, str(word_count), status, recommendation])
                
                # Color-code the status column
                if word_count < 300:
                    item.setForeground(2, Qt.GlobalColor(Qt.red))
                elif word_count < 500:
                    item.setForeground(2, Qt.GlobalColor(Qt.darkYellow))
                elif word_count < 1000:
                    item.setForeground(2, Qt.GlobalColor(Qt.darkGreen))
                else:
                    item.setForeground(2, Qt.GlobalColor(Qt.blue))
                
                self.results_tree.addTopLevelItem(item)
                
                self.analysis_results.append({
                    'file': rel_path,
                    'words': word_count,
                    'status': status
                })
                
            except Exception as e:
                # Add error item
                item = QTreeWidgetItem([str(html_path.name), "Error", "❌ Parse Error", str(e)[:50]])
                item.setForeground(2, Qt.GlobalColor(Qt.red))
                self.results_tree.addTopLevelItem(item)
            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        # Calculate statistics
        avg_words = total_words // len(html_files) if html_files else 0
        
        self.total_pages_label.setText(f"Total pages: {len(html_files)}")
        self.avg_length_label.setText(f"Avg length: {avg_words} words")
        self.short_pages_label.setText(f"Short pages: {short_count}")
        
        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        # Expand all items so user can see them
        self.results_tree.expandAll()
        
        # Color-code stats based on average
        if avg_words < 300:
            avg_color = "red"
        elif avg_words < 500:
            avg_color = "orange"
        elif avg_words < 1000:
            avg_color = "green"
        else:
            avg_color = "blue"
        
        self.summary_label.setText(
            f"✅ Analysis complete! Found {len(html_files)} pages. "
            f"Average: {avg_words} words. {short_count} pages need improvement."
        )
        
        QMessageBox.information(self, "Analysis Complete", 
            f"📊 Content Length Analysis\n\n"
            f"Total pages: {len(html_files)}\n"
            f"Average length: {avg_words} words\n"
            f"Pages needing improvement: {short_count}\n\n"
            f"📋 Check the results table above for details on each page.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            # Dark theme styles
            self.results_tree.setStyleSheet("""
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
            self.guidelines.setStyleSheet("""
                padding: 8px; 
                border-radius: 4px; 
                margin-top: 5px;
                background-color: #1E1F22;
                color: #E8E8E8;
                border: 1px solid #3E4045;
            """)
        else:
            # Light theme styles
            self.results_tree.setStyleSheet("""
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
            self.guidelines.setStyleSheet("""
                padding: 8px; 
                border-radius: 4px; 
                margin-top: 5px;
                background-color: #F8F9FA;
                color: #2C3E50;
                border: 1px solid #D0D7DE;
            """)
