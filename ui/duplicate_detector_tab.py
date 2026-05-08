from pathlib import Path
from collections import defaultdict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox  # ← Added QMessageBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class DuplicateDetectorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan Duplicates")
        self.scan_btn.clicked.connect(self.scan)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Issue Type", "Content", "Files"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.results_tree)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.summary_label = QLabel("Ready - Select a folder and click Scan Duplicates")
        layout.addWidget(self.summary_label)

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

                title_tag = soup.find('title')
                if title_tag and title_tag.string:
                    titles[title_tag.string.strip()].append(html_path.name)

                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    descriptions[meta_desc['content'].strip()].append(html_path.name)

                h1_tag = soup.find('h1')
                if h1_tag and h1_tag.get_text(strip=True):
                    h1s[h1_tag.get_text(strip=True)].append(html_path.name)
            except Exception:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        duplicate_count = 0
        for title, files in titles.items():
            if len(files) > 1:
                item = QTreeWidgetItem(["Duplicate Title", title[:100], ", ".join(files)])
                self.results_tree.addTopLevelItem(item)
                duplicate_count += 1

        for desc, files in descriptions.items():
            if len(files) > 1:
                item = QTreeWidgetItem(["Duplicate Description", desc[:100], ", ".join(files)])
                self.results_tree.addTopLevelItem(item)
                duplicate_count += 1

        for h1, files in h1s.items():
            if len(files) > 1:
                item = QTreeWidgetItem(["Duplicate H1", h1[:100], ", ".join(files)])
                self.results_tree.addTopLevelItem(item)
                duplicate_count += 1

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if duplicate_count == 0:
            self.summary_label.setText(f"✅ Great! No duplicate issues found across {len(html_files)} files")
        else:
            self.summary_label.setText(f"⚠️ Found {duplicate_count} duplicate issues across {len(html_files)} files")

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
