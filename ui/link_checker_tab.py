import os
import requests
from pathlib import Path
from urllib.parse import urlparse
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QProgressBar, QGroupBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QApplication, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from bs4 import BeautifulSoup


class LinkCheckerWorker(QThread):
    progress = Signal(int)
    result = Signal(dict)
    finished_signal = Signal()
    
    def __init__(self, project_folder, check_external):
        super().__init__()
        self.project_folder = project_folder
        self.check_external = check_external
        self.results = []
        
    def run(self):
        html_files = list(Path(self.project_folder).rglob("*.html"))
        total = len(html_files)
        
        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))
                
                # Find all links
                for tag in soup.find_all(['a', 'link', 'script', 'img']):
                    for attr in ['href', 'src']:
                        if tag.has_attr(attr):
                            link = tag[attr]
                            if not link or link.startswith('#') or link.startswith('javascript:'):
                                continue
                            
                            # Determine if internal or external
                            is_external = link.startswith('http://') or link.startswith('https://')
                            
                            if not is_external:
                                # Internal link - check if file exists
                                link_path = self.resolve_internal_link(html_path, link)
                                if link_path and not link_path.exists():
                                    self.results.append({
                                        "type": "Broken Internal Link",
                                        "file": rel_path,
                                        "element": f"<{tag.name}>",
                                        "link": link,
                                        "details": f"File not found: {link}"
                                    })
                            elif self.check_external:
                                # External link - optional check
                                is_valid = self.check_external_link(link)
                                if not is_valid:
                                    self.results.append({
                                        "type": "Broken External Link",
                                        "file": rel_path,
                                        "element": f"<{tag.name}>",
                                        "link": link,
                                        "details": "Failed to reach URL (timeout or 404)"
                                    })
            except Exception as e:
                self.results.append({
                    "type": "Parse Error",
                    "file": rel_path,
                    "element": "",
                    "link": "",
                    "details": str(e)[:100]
                })
            
            self.progress.emit(int((idx + 1) / total * 100))
        
        self.finished_signal.emit()
    
    def resolve_internal_link(self, html_path, link):
        """Resolve internal link to absolute filesystem path."""
        # Remove query parameters and anchors
        link = link.split('?')[0].split('#')[0]
        if not link or link.strip() == '':
            return None
        
        # Try different path resolutions
        candidates = [
            html_path.parent / link,
            Path(self.project_folder) / link,
            Path(self.project_folder) / link.lstrip('/'),
            html_path.parent / link.replace('../', ''),
        ]
        
        for candidate in candidates:
            try:
                resolved = candidate.resolve()
                if resolved.exists():
                    return resolved
            except:
                continue
        return None
    
    def check_external_link(self, url):
        """Check if external URL is reachable."""
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except:
            try:
                response = requests.get(url, timeout=5, stream=True)
                return response.status_code < 400
            except:
                return False


class LinkCheckerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.worker = None
        self.results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for Broken Links")
        self.scan_btn.clicked.connect(self.scan_links)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Options
        opts_group = QGroupBox("Scan Options")
        opts_layout = QHBoxLayout()
        self.check_external = QCheckBox("Check external links (requires internet, slower)")
        self.check_external.setChecked(False)
        opts_layout.addWidget(self.check_external)
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Type", "File", "Element", "Broken Link", "Details"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Summary
        self.summary_label = QLabel("Ready - Select a folder and click Scan")
        layout.addWidget(self.summary_label)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def scan_links(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.results_tree.clear()
        self.results = []

        # Start worker thread
        self.worker = LinkCheckerWorker(self.project_folder, self.check_external.isChecked())
        self.worker.progress.connect(self.update_progress)
        self.worker.finished_signal.connect(self.scan_finished)
        self.worker.start()

        self.summary_label.setText("Scanning for broken links...")

    def update_progress(self, value):
        self.progress.setValue(value)

    def scan_finished(self):
        self.results = self.worker.results
        
        for result in self.results:
            item = QTreeWidgetItem([
                result["type"],
                result["file"],
                result["element"],
                result["link"],
                result["details"]
            ])
            # Color broken links red
            if "Broken" in result["type"]:
                for col in range(5):
                    item.setForeground(col, Qt.red)
            self.results_tree.addTopLevelItem(item)
        
        total_broken = len([r for r in self.results if "Broken" in r["type"]])
        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if total_broken == 0:
            self.summary_label.setText(f"✅ Scan complete! No broken links found.")
        else:
            self.summary_label.setText(f"⚠️ Scan complete! Found {total_broken} broken links.")
        
        QMessageBox.information(self, "Scan Complete", 
                                f"Found {total_broken} broken links.\n"
                                f"Check the results panel for details.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    alternate-background-color: #3E4045;
                    background-color: #2B2D31;
                    color: #E8E8E8;
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
                    alternate-background-color: #F8F9FA;
                    background-color: #FFFFFF;
                    color: #2C3E50;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
