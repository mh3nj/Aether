"""
Aether SEO API Tab – PageSpeed Insights & Core Web Vitals
Fetches real performance data from Google's API
"""

import requests
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QPlainTextEdit, QMessageBox, QGroupBox,
    QLineEdit, QProgressBar, QComboBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QThread, Signal


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
                result = f"\uf080 PageSpeed Insights for: {self.url}\n"
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
                    fid = data['lighthouseResult']['audits'].get('max-potential-fid', {})
                    
                    result += "\n=== METRICS ===\n"
                    if cls.get('displayValue'):
                        result += f"CLS: {cls['displayValue']}\n"
                    if lcp.get('displayValue'):
                        result += f"LCP: {lcp['displayValue']}\n"
                    if fid.get('displayValue'):
                        result += f"FID: {fid['displayValue']}\n"
                
                self.finished.emit(result)
            else:
                self.error.emit(f"API Error: {data.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            self.error.emit(str(e))


class SEOAPITab(QWidget):
    def __init__(self):
        super().__init__()
        self.pagespeed_score = 0
        self.data_bridge = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # URL input
        url_group = QGroupBox("Website URL")
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setMinimumHeight(30)
        self.test_btn = QPushButton("\uf080 Run PageSpeed Test")
        self.test_btn.clicked.connect(self.run_pagespeed)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.test_btn)
        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

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
        layout.addWidget(strategy_group)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Results area
        self.results = QPlainTextEdit()
        self.results.setReadOnly(True)
        font = QFont("Courier New", 10)
        self.results.setFont(font)
        layout.addWidget(self.results)

        # Explanation
        info_label = QLabel(
            "💡 PageSpeed Insights analyzes your website's performance and provides Core Web Vitals metrics.\n"
            "• LCP (Largest Contentful Paint): Loading performance\n"
            "• CLS (Cumulative Layout Shift): Visual stability\n"
            "• FID (First Input Delay): Interactivity\n\n"
            "Score ranges: 0-49 (Poor), 50-89 (Needs Improvement), 90-100 (Good)"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #8095AB; padding: 10px;")
        layout.addWidget(info_label)

        self.status_label = QLabel("Ready - Enter a URL and click Run PageSpeed Test")
        layout.addWidget(self.status_label)

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge

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
        self.progress.setVisible(True)
        self.results.clear()
        self.results.appendPlainText(f"\uf002 Testing: {url}\n")
        self.results.appendPlainText("=" * 60 + "\n")
        
        strategy = self.get_strategy()
        self.results.appendPlainText(f"\uf080 Fetching PageSpeed Insights ({strategy.upper()})...\n")
        
        self.worker = PageSpeedWorker(url, strategy)
        self.worker.finished.connect(self.on_pagespeed_result)
        self.worker.error.connect(self.on_pagespeed_error)
        self.worker.start()

    def on_pagespeed_result(self, result):
        self.results.appendPlainText(result)
        self.results.appendPlainText("\n" + "=" * 60)
        self.results.appendPlainText("\n \uf0eb For full report, visit: https://pagespeed.web.dev/")
        self.progress.setVisible(False)
        self.test_btn.setEnabled(True)
        self.status_label.setText("PageSpeed test completed")
        
        # Extract score for dashboard
        import re
        match = re.search(r'Performance: (\d+)/100', result)
        if match:
            self.pagespeed_score = int(match.group(1))
            if self.data_bridge:
                self.data_bridge.report_scan(1, 0, self.pagespeed_score)

    def on_pagespeed_error(self, error):
        self.results.appendPlainText(f"\58 Error: {error}")
        self.results.appendPlainText("\n \uf0eb This might be due to:\n")
        self.results.appendPlainText("• Invalid URL (make sure it's reachable)\n")
        self.results.appendPlainText("• Rate limiting (try again in a minute)\n")
        self.results.appendPlainText("• The website might be blocking bots")
        self.progress.setVisible(False)
        self.test_btn.setEnabled(True)
        self.status_label.setText("Error occurred - check URL and try again")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.results.setStyleSheet("background-color: #2B2D31; color: #E8E8E8;")
        else:
            self.results.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")
