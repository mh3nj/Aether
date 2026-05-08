"""
Aether Performance Lab – Preload scanner and PageSpeed Insights
Merged tab for performance optimization tools
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QGroupBox, QCheckBox,
    QTabWidget, QMessageBox, QPlainTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from bs4 import BeautifulSoup
import requests


class PageSpeedWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, url, strategy="mobile"):
        super().__init__()
        self.url = url
        self.strategy = strategy
    
    def run(self):
        try:
            api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={self.url}&strategy={self.strategy}"
            response = requests.get(api_url, timeout=30)
            data = response.json()
            
            if 'lighthouseResult' in data:
                result = f"📊 PageSpeed Insights for: {self.url}\n"
                result += f"Strategy: {self.strategy.upper()}\n\n"
                
                scores = data['lighthouseResult']['categories']
                result += "=== CORE WEB VITALS ===\n"
                result += f"Performance: {scores['performance']['score'] * 100:.0f}/100\n"
                result += f"Accessibility: {scores['accessibility']['score'] * 100:.0f}/100\n"
                result += f"Best Practices: {scores['best-practices']['score'] * 100:.0f}/100\n"
                result += f"SEO: {scores['seo']['score'] * 100:.0f}/100\n"
                
                if 'audits' in data['lighthouseResult']:
                    cls = data['lighthouseResult']['audits'].get('cumulative-layout-shift', {})
                    lcp = data['lighthouseResult']['audits'].get('largest-contentful-paint', {})
                    
                    result += "\n=== METRICS ===\n"
                    if cls.get('displayValue'):
                        result += f"CLS: {cls['displayValue']}\n"
                    if lcp.get('displayValue'):
                        result += f"LCP: {lcp['displayValue']}\n"
                
                self.finished.emit(result)
            else:
                self.error.emit(f"API Error: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            self.error.emit(str(e))


class PerformanceLabTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.preloads = []
        self.pagespeed_worker = None
        self.data_bridge = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget for sub-tools
        self.perf_tabs = QTabWidget()
        layout.addWidget(self.perf_tabs)
        
        # ========== TAB 1: PRELOAD SCANNER ==========
        preload_tab = QWidget()
        preload_layout = QVBoxLayout(preload_tab)
        
        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("📁 Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("🔍 Scan for Preload Opportunities")
        self.scan_btn.clicked.connect(self.scan_preloads)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        preload_layout.addLayout(folder_row)
        
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
        preload_layout.addWidget(opts_group)
        
        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Asset", "Type", "Action"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.setAlternatingRowColors(True)
        preload_layout.addWidget(self.results_tree)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        preload_layout.addWidget(self.progress)
        
        # Inject button
        self.inject_btn = QPushButton("🚀 Inject Preload Links into HTML")
        self.inject_btn.clicked.connect(self.inject_preloads)
        self.inject_btn.setEnabled(False)
        preload_layout.addWidget(self.inject_btn)
        
        self.perf_tabs.addTab(preload_tab, "⚡ Preload Scanner")
        
        # ========== TAB 2: PAGESPEED INSIGHTS ==========
        pagespeed_tab = QWidget()
        pagespeed_layout = QVBoxLayout(pagespeed_tab)
        
        # URL input
        url_group = QGroupBox("Website URL")
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setMinimumHeight(30)
        self.test_btn = QPushButton("📊 Run PageSpeed Test")
        self.test_btn.clicked.connect(self.run_pagespeed)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.test_btn)
        url_group.setLayout(url_layout)
        pagespeed_layout.addWidget(url_group)
        
        # Strategy selection
        strategy_group = QGroupBox("Test Strategy")
        strategy_layout = QHBoxLayout()
        self.mobile_btn = QPushButton("📱 Mobile")
        self.mobile_btn.setCheckable(True)
        self.mobile_btn.setChecked(True)
        self.desktop_btn = QPushButton("💻 Desktop")
        self.desktop_btn.setCheckable(True)
        strategy_layout.addWidget(self.mobile_btn)
        strategy_layout.addWidget(self.desktop_btn)
        strategy_group.setLayout(strategy_layout)
        pagespeed_layout.addWidget(strategy_group)
        
        # Results area
        self.pagespeed_results = QPlainTextEdit()
        self.pagespeed_results.setReadOnly(True)
        pagespeed_layout.addWidget(self.pagespeed_results)
        
        self.perf_tabs.addTab(pagespeed_tab, "📊 PageSpeed Insights")
        
        # Status
        self.status_label = QLabel("Ready - Select a folder or enter a URL")
        layout.addWidget(self.status_label)

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def scan_preloads(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.status_label.setText("No HTML files found.")
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

                # CSS files
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
                                item = QTreeWidgetItem([rel_path, href, 'CSS', '⚡ Preload as style'])
                                self.results_tree.addTopLevelItem(item)

                # JavaScript files
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
                                    item = QTreeWidgetItem([rel_path, src, 'JavaScript', '⚡ Preload as script'])
                                    self.results_tree.addTopLevelItem(item)

                # Hero images
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
                                item = QTreeWidgetItem([rel_path, src, 'Hero Image', '⚡ Preload as image'])
                                self.results_tree.addTopLevelItem(item)

                # Web fonts
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
                            item = QTreeWidgetItem([rel_path, href, 'Web Font', '⚡ Preload as font'])
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
            self.status_label.setText(f"✅ Found {len(self.preloads)} preload opportunities across {len(html_files)} files")
            QMessageBox.information(self, "Scan Complete", 
                f"Found {len(self.preloads)} assets that can be preloaded.\n\n"
                f"Click 'Inject Preload Links' to add them to your HTML files.\n\n"
                f"This will improve your Largest Contentful Paint (LCP) score.")
        else:
            self.inject_btn.setEnabled(False)
            self.status_label.setText(f"✅ No preload opportunities found. Your site is already optimized!")

    def inject_preloads(self):
        if not self.preloads:
            QMessageBox.warning(self, "Warning", "No preloads to inject. Run scan first.")
            return

        reply = QMessageBox.question(self, "Confirm Injection",
                                     f"Inject {len(self.preloads)} preload links into your HTML files?\n\n"
                                     f"This will add <link rel='preload'> tags to the <head> of each file.\n\n"
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

                # Check if already preloaded
                existing = head.find('link', rel='preload', href=preload['asset'])
                if not existing:
                    preload_tag = soup.new_tag('link', rel='preload', href=preload['asset'], as_=preload['as_type'])
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
            f"Injected {injected} preload links into HTML files.\n\n"
            f"💡 Tip: Run Lighthouse in Chrome DevTools to see the improvement!")
        self.status_label.setText(f"✅ Injected {injected} preload links")

    def get_strategy(self):
        if self.mobile_btn.isChecked():
            return "mobile"
        return "desktop"

    def run_pagespeed(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Enter a URL first.")
            return
        
        if not url.startswith("http"):
            url = "https://" + url
        
        self.test_btn.setEnabled(False)
        self.pagespeed_results.clear()
        self.pagespeed_results.appendPlainText(f"🔍 Testing: {url}\n")
        self.pagespeed_results.appendPlainText("=" * 60 + "\n")
        
        strategy = self.get_strategy()
        self.pagespeed_results.appendPlainText(f"📊 Fetching PageSpeed Insights ({strategy.upper()})...\n")
        
        self.pagespeed_worker = PageSpeedWorker(url, strategy)
        self.pagespeed_worker.finished.connect(self.on_pagespeed_result)
        self.pagespeed_worker.error.connect(self.on_pagespeed_error)
        self.pagespeed_worker.start()

    def on_pagespeed_result(self, result):
        self.pagespeed_results.appendPlainText(result)
        self.pagespeed_results.appendPlainText("\n" + "=" * 60)
        self.pagespeed_results.appendPlainText("\n💡 For full report, visit: https://pagespeed.web.dev/")
        self.test_btn.setEnabled(True)
        self.status_label.setText("PageSpeed test completed")
        
        # Extract score for dashboard
        if self.data_bridge:
            import re
            match = re.search(r'Performance: (\d+)/100', result)
            if match:
                score = int(match.group(1))
                self.data_bridge.report_scan(1, 0, score)

    def on_pagespeed_error(self, error):
        self.pagespeed_results.appendPlainText(f"❌ Error: {error}")
        self.test_btn.setEnabled(True)
        self.status_label.setText("Error occurred")

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
            self.pagespeed_results.setStyleSheet("background-color: #2B2D31; color: #E8E8E8;")
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
            self.pagespeed_results.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")
