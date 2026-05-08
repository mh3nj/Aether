"""
Aether Duplicate Detector - Find duplicate titles, descriptions, and H1 tags across HTML files
"""

from pathlib import Path
from collections import defaultdict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class DuplicateDetectorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.data_bridge = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("\f07c Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("\f1b8 Scan Duplicates")
        self.scan_btn.clicked.connect(self.scan)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Issue Type", "Content", "Files"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_tree.setAlternatingRowColors(True)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Summary
        self.summary_label = QLabel("Ready - Select a folder and click Scan Duplicates")
        layout.addWidget(self.summary_label)

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def scan(self):
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

        titles = defaultdict(list)
        descriptions = defaultdict(list)
        h1s = defaultdict(list)

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                # Extract title
                title_tag = soup.find('title')
                if title_tag and title_tag.string:
                    title_content = title_tag.string.strip()
                    if title_content:
                        titles[title_content].append(html_path.name)

                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    desc_content = meta_desc['content'].strip()
                    if desc_content:
                        descriptions[desc_content].append(html_path.name)

                # Extract H1
                h1_tag = soup.find('h1')
                if h1_tag and h1_tag.get_text(strip=True):
                    h1_content = h1_tag.get_text(strip=True)
                    if h1_content:
                        h1s[h1_content].append(html_path.name)
                        
            except Exception:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        duplicate_count = 0
        
        # Add duplicate titles to tree
        for title, files in titles.items():
            if len(files) > 1:
                item = QTreeWidgetItem(["\f31c Duplicate Title", title[:100], ", ".join(files)])
                self.results_tree.addTopLevelItem(item)
                duplicate_count += 1

        # Add duplicate descriptions to tree
        for desc, files in descriptions.items():
            if len(files) > 1:
                item = QTreeWidgetItem(["\f15c Duplicate Description", desc[:100], ", ".join(files)])
                self.results_tree.addTopLevelItem(item)
                duplicate_count += 1

        # Add duplicate H1s to tree
        for h1, files in h1s.items():
            if len(files) > 1:
                item = QTreeWidgetItem(["\f02b Duplicate H1", h1[:100], ", ".join(files)])
                self.results_tree.addTopLevelItem(item)
                duplicate_count += 1

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        # Report to dashboard
        if self.data_bridge:
            self.data_bridge.report_scan(len(html_files), duplicate_count, 0)
        
        self.results_tree.expandAll()
        
        if duplicate_count == 0:
            self.summary_label.setText(f"\f00c Great! No duplicate issues found across {len(html_files)} files")
        else:
            self.summary_label.setText(f"\f071 Found {duplicate_count} duplicate issues across {len(html_files)} files")
            
            QMessageBox.warning(self, "Duplicate Content Found", 
                f"Found {duplicate_count} duplicate content issues!\n\n"
                f"• Duplicate titles: {len(titles)}\n"
                f"• Duplicate descriptions: {len(descriptions)}\n"
                f"• Duplicate H1s: {len(h1s)}\n\n"
                f"Duplicate content can harm SEO rankings. "
                f"Use unique titles and descriptions for each page.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
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
        else:
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
