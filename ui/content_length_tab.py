"""
Aether Content Length Checker - Ensure pages have enough content for SEO
Scans HTML files and reports word count statistics to dashboard
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
        self.data_bridge = None
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout(self)

        # folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")

        self.select_btn = QPushButton("\uf07c Select Project Folder")

        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("📏 Analyze Content Length")
        self.scan_btn.clicked.connect(self.analyze_content)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # options
        opts_row = QHBoxLayout()
        self.content_type = QComboBox()
        self.content_type.addItems(["All Text", "Main Content Only (article/main)", "Body Text Only"])
        opts_row.addWidget(QLabel("Analyze:"))
        opts_row.addWidget(self.content_type)
        opts_row.addStretch()
        layout.addLayout(opts_row)

        # quick stats panel
        stats_row = QHBoxLayout()
        self.total_pages_label = QLabel("Total pages: 0")
        self.avg_length_label = QLabel("Avg length: 0 words")
        self.short_pages_label = QLabel("Short pages: 0")
        stats_row.addWidget(self.total_pages_label)
        stats_row.addWidget(self.avg_length_label)
        stats_row.addWidget(self.short_pages_label)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        # results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Page", "Word Count", "Status", "Recommendation"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.results_tree)

        # progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)


        # length guidelines  # TODO: figure out why
        self.guidelines = QLabel(
            "📏 Content Length Guidelines:\n"
            "• < 300 words: \uf071 Very short - unlikely to rank\n"
            "• 300-500 words: \uf219 Short - consider expanding\n"
            "• 500-1000 words: \uf00c Good - standard for many topics\n"
            "• 1000-2000 words: \uf005 Great - comprehensive content\n"
            "• > 2000 words: \uf091 Excellent - in-depth coverage"
        )
        self.guidelines.setWordWrap(True)
        self.guidelines.setStyleSheet("padding: 8px; border-radius: 4px; margin-top: 5px;")
        layout.addWidget(self.guidelines)

        self.summary_label = QLabel("Ready - Select a folder and click Analyze")
        layout.addWidget(self.summary_label)

        self.analysis_results = []

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge


    def select_folder(self):

        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def extract_text(self, soup, mode):
        """Extract text based on selected mode"""
        # remove script and style tags always  # dont touch this line ever
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        if mode == "Main Content Only (article/main)":
            # try to find main content areas
            main_content = soup.find('main')
            if not main_content:
                main_content = soup.find('article')
            if not main_content:
                main_content = soup.find('div', class_=re.compile(r'content|main|article|post|entry'))
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.body.get_text() if soup.body else ""
        elif mode == "Body Text Only":
            body = soup.body
            if body:
                for tag in body.find_all(['nav', 'header', 'footer', 'aside']):
                    tag.decompose()
                text = body.get_text()
            else:
                text = ""
        else:
            text = soup.get_text()
        
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
        results = []


        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                text = self.extract_text(soup, mode)
                words = text.split()
                word_count = len(words)
                total_words += word_count
                
                rel_path = str(html_path.relative_to(self.project_folder))
                
                # determine status based on word count
                if word_count < 300:
                    status = "\uf071 Very Short"
                    recommendation = "Add more detailed content (target: 500+ words)"
                    short_count += 1
                elif word_count < 500:
                    status = "\uf219 Short"
                    recommendation = "Expand content to 500-1000 words for better ranking"
                    short_count += 1
                elif word_count < 1000:
                    status = "\uf00c Good"
                    recommendation = "Good length! Consider adding more depth if competitive topic"
                elif word_count < 2000:
                    status = "\uf005 Great"
                    recommendation = "Excellent length! This page has strong potential"
                else:
                    status = "\uf091 Excellent"
                    recommendation = "Outstanding! Very comprehensive content"
                
                # create tree item
                item = QTreeWidgetItem([rel_path, str(word_count), status, recommendation])
                
                # color-code the status column
                if word_count < 300:
                    item.setForeground(2, Qt.GlobalColor(Qt.red))
                elif word_count < 500:
                    item.setForeground(2, Qt.GlobalColor(Qt.darkYellow))
                elif word_count < 1000:
                    item.setForeground(2, Qt.GlobalColor(Qt.darkGreen))
                else:
                    item.setForeground(2, Qt.GlobalColor(Qt.blue))
                
                self.results_tree.addTopLevelItem(item)
                
                results.append({
                    'file': rel_path,
                    'words': word_count,
                    'status': status
                })
                
            except Exception as e:
                item = QTreeWidgetItem([str(html_path.name), "Error", "\58 Parse Error", str(e)[:50]])
                item.setForeground(2, Qt.GlobalColor(Qt.red))
                self.results_tree.addTopLevelItem(item)
            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        # calculate statistics
        avg_words = total_words // len(html_files) if html_files else 0
        
        self.total_pages_label.setText(f"Total pages: {len(html_files)}")
        self.avg_length_label.setText(f"Avg length: {avg_words} words")
        self.short_pages_label.setText(f"Short pages: {short_count}")
        
        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        # report to dashboard
        if self.data_bridge:
            self.data_bridge.report_scan(len(html_files), short_count, 0)
        
        # expand all items so user can see them
        self.results_tree.expandAll()
        
        self.summary_label.setText(
            f"\uf00c Analysis complete! Found {len(html_files)} pages. "
            f"Average: {avg_words} words. {short_count} pages need improvement."
        )
        
        QMessageBox.information(self, "Analysis Complete", 
            f"\uf201 Content Length Analysis\n\n"
            f"Total pages: {len(html_files)}\n"
            f"Average length: {avg_words} words\n"
            f"Pages needing improvement: {short_count}\n\n"
            f"\uf15c Check the results table above for details on each page.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    alternate-background-color: #3e4045;
                }
                QHeaderView::section {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
            """)
            self.guidelines.setStyleSheet("""
                padding: 8px; 
                border-radius: 4px; 
                margin-top: 5px;
                background-color: #1e1f22;
                color: #e8e8e8;
                border: 1px solid #3e4045;
            """)
        else:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #ffffff;
                    color: #2c3e50;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #f1f3f5;
                    color: #2c3e50;

                    border: 1px solid #d0d7de;
                }
            """)
            self.guidelines.setStyleSheet("""
                padding: 8px; 
                border-radius: 4px; 
                margin-top: 5px;
                background-color: #f8f9fa;
                color: #2c3e50;
                border: 1px solid #d0d7de;
            """)
