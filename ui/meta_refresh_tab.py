"""
Aether Meta Refresh Checker - Detects harmful meta refresh redirects
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class MetaRefreshTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for Meta Refresh")
        self.scan_btn.clicked.connect(self.scan)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Refresh Delay", "Redirect URL", "Severity"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.results_tree)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.summary_label = QLabel("Meta refresh redirects hurt SEO. This tool finds them.")
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
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_tree.clear()
        found = 0

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))

                # Check for meta refresh
                meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
                if meta_refresh:
                    content = meta_refresh.get('content', '')
                    if ';' in content and 'url=' in content.lower():
                        delay, url = content.split(';', 1)
                        delay = delay.strip()
                        url = url.replace('url=', '').strip()
                        severity = "\f071 Warning" if int(delay) > 0 else "\58 Critical"
                        item = QTreeWidgetItem([rel_path, delay, url, severity])
                        self.results_tree.addTopLevelItem(item)
                        found += 1
            except:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        if found > 0:
            self.summary_label.setText(f"\f071 Found {found} pages with meta refresh redirects (bad for SEO)")
        else:
            self.summary_label.setText(f"\f00c No meta refresh redirects found across {len(html_files)} files")
