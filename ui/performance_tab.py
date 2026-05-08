"""
Aether Performance Tab - Preload Scanner & Injector
Optimizes page load speed by adding preload links for critical assets
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QGroupBox, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class PerformanceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.preloads = []
        self.data_bridge = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("\e185 Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("\uf002 Scan for Preload Opportunities")
        self.scan_btn.clicked.connect(self.scan)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Options
        opts_group = QGroupBox("Scan Options")
        opts_layout = QHBoxLayout()
        self.check_css = QCheckBox("CSS files")
        self.check_css.setChecked(True)
        self.check_js = QCheckBox("JavaScript files")
        self.check_js.setChecked(True)
        self.check_images = QCheckBox("Hero images (first 3 per page)")
        self.check_images.setChecked(True)
        self.check_fonts = QCheckBox("Web fonts")
        self.check_fonts.setChecked(True)
        opts_layout.addWidget(self.check_css)
        opts_layout.addWidget(self.check_js)
        opts_layout.addWidget(self.check_images)
        opts_layout.addWidget(self.check_fonts)
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Asset", "Type", "Action"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.setAlternatingRowColors(True)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Inject button
        self.inject_btn = QPushButton("\uf135 Inject Preload Links into HTML")
        self.inject_btn.clicked.connect(self.inject_preloads)
        self.inject_btn.setEnabled(False)
        layout.addWidget(self.inject_btn)

        # Summary
        self.summary_label = QLabel("Ready - Select a folder and click Scan")
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
        self.preloads = []

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))

                # 1. Check CSS files
                if self.check_css.isChecked():
                    for link in soup.find_all('link', rel='stylesheet'):
                        href = link.get('href')
                        if href and not href.startswith('http') and not href.startswith('//'):
                            if not href.startswith('data:'):
                                self.preloads.append({
                                    'file': rel_path,
                                    'full_path': html_path,
                                    'asset': href,
                                    'type': 'CSS',
                                    'as_type': 'style'
                                })
                                item = QTreeWidgetItem([rel_path, href, 'CSS', '\uf0e7 Preload as style'])
                                self.results_tree.addTopLevelItem(item)

                # 2. Check JS files (not async/defer)
                if self.check_js.isChecked():
                    for script in soup.find_all('script', src=True):
                        src = script.get('src')
                        if src and not src.startswith('http') and not src.startswith('//'):
                            if not script.get('async') and not script.get('defer'):
                                if not src.startswith('data:'):
                                    self.preloads.append({
                                        'file': rel_path,
                                        'full_path': html_path,
                                        'asset': src,
                                        'type': 'JavaScript',
                                        'as_type': 'script'
                                    })
                                    item = QTreeWidgetItem([rel_path, src, 'JavaScript', '\uf0e7 Preload as script'])
                                    self.results_tree.addTopLevelItem(item)

                # 3. Check hero images (first 3)
                if self.check_images.isChecked():
                    for i, img in enumerate(soup.find_all('img')[:3]):
                        src = img.get('src')
                        if src and not src.startswith('http') and not src.startswith('//'):
                            if not src.startswith('data:'):
                                self.preloads.append({
                                    'file': rel_path,
                                    'full_path': html_path,
                                    'asset': src,
                                    'type': 'Hero Image',
                                    'as_type': 'image'
                                })
                                item = QTreeWidgetItem([rel_path, src, 'Hero Image', '\uf0e7 Preload as image'])
                                self.results_tree.addTopLevelItem(item)

                # 4. Check web fonts
                if self.check_fonts.isChecked():
                    for link in soup.find_all('link', href=True):
                        href = link.get('href')
                        if href and ('.woff' in href or '.woff2' in href or '.ttf' in href or '.otf' in href):
                            self.preloads.append({
                                'file': rel_path,
                                'full_path': html_path,
                                'asset': href,
                                'type': 'Web Font',
                                'as_type': 'font',
                                'crossorigin': 'anonymous'
                            })
                            item = QTreeWidgetItem([rel_path, href, 'Web Font', '\uf0e7 Preload as font'])
                            self.results_tree.addTopLevelItem(item)

            except Exception:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)

        # Report to dashboard
        if self.data_bridge:
            self.data_bridge.report_scan(len(html_files), len(self.preloads), 0)

        if self.preloads:
            self.inject_btn.setEnabled(True)
            self.summary_label.setText(f"\uf00c Found {len(self.preloads)} preload opportunities across {len(html_files)} files")
            QMessageBox.information(self, "Scan Complete", 
                f"Found {len(self.preloads)} assets that can be preloaded.\n\n"
                f"Click 'Inject Preload Links' to add them to your HTML files.")
        else:
            self.inject_btn.setEnabled(False)
            self.summary_label.setText(f"\uf00c No preload opportunities found. Your site is already optimized!")

    def inject_preloads(self):
        if not self.preloads:
            QMessageBox.warning(self, "Warning", "No preloads to inject. Run scan first.")
            return

        reply = QMessageBox.question(self, "Confirm Injection",
                                     f"Inject {len(self.preloads)} preload links into your HTML files?\n\n"
                                     f"Proceed?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.inject_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.preloads))

        injected = 0
        for idx, preload in enumerate(self.preloads):
            try:
                with open(preload['full_path'], 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')

                head = soup.head
                if not head:
                    head = soup.new_tag('head')
                    soup.html.insert(0, head)

                existing = head.find('link', rel='preload', href=preload['asset'])
                if not existing:
                    preload_tag = soup.new_tag('link', 
                                               rel='preload', 
                                               href=preload['asset'], 
                                               as_=preload['as_type'])
                    if preload.get('crossorigin'):
                        preload_tag['crossorigin'] = preload['crossorigin']
                    head.append(preload_tag)
                    injected += 1

                with open(preload['full_path'], 'w', encoding='utf-8') as f:
                    f.write(str(soup))

            except Exception:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.inject_btn.setEnabled(True)
        
        # Report to dashboard
        if self.data_bridge and injected > 0:
            self.data_bridge.report_fix("preload", injected)
        
        QMessageBox.information(self, "Injection Complete", 
            f"Injected {injected} preload links into HTML files.")
        self.summary_label.setText(f"\uf00c Injected {injected} preload links")

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
