"""
Aether Performance Lab – Preload scanner and PageSpeed Insights
Merged tab for performance optimization tools
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QGroupBox, QCheckBox,
    QTabWidget, QMessageBox, QPlainTextEdit, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from bs4 import BeautifulSoup
import requests

# import standalone tabs
from ui.performance_tab import PerformanceTab
from ui.seo_api_tab import SEOAPITab


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
                result = f"\uf201 PageSpeed Insights for: {self.url}\n"
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
        
        # create tab widget for sub-tools  # spaghetti code
        self.perf_tabs = QTabWidget()
        layout.addWidget(self.perf_tabs)
        
        # ========== tab 1: preload scanner ==========
        preload_tab = QWidget()
        preload_layout = QVBoxLayout(preload_tab)
        
        # embed the standalone performancetab
        self.performance_tab = PerformanceTab()
        preload_layout.addWidget(self.performance_tab)
        
        self.perf_tabs.addTab(preload_tab, "\uf0e7 Preload Scanner")
        
        # ========== tab 2: pagespeed insights ==========
        pagespeed_tab = QWidget()
        pagespeed_layout = QVBoxLayout(pagespeed_tab)
        
        # embed the standalone seoapitab
        self.seo_api_tab = SEOAPITab()
        pagespeed_layout.addWidget(self.seo_api_tab)
        
        self.perf_tabs.addTab(pagespeed_tab, "\uf201 PageSpeed Insights")
        
        # status  # temporary solution
        self.status_label = QLabel("Ready - Select a folder or enter a URL")
        layout.addWidget(self.status_label)

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge
        # propagate to child tabs
        if hasattr(self.performance_tab, 'set_data_bridge'):
            self.performance_tab.set_data_bridge(bridge)
        if hasattr(self.seo_api_tab, 'set_data_bridge'):
            self.seo_api_tab.set_data_bridge(bridge)

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        # style the main tab widget
        if is_dark:
            self.perf_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #1e1f22;
                    border: 1px solid #3e4045;
                }
                QTabBar::tab {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #3e4045;
                }
                QTabBar::tab:hover {
                    background-color: #4b4e54;
                }
            """)
        else:
            self.perf_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #ffffff;
                    border: 1px solid #d0d7de;
                }
                QTabBar::tab {
                    background-color: #f1f3f5;
                    color: #2c3e50;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {

                    background-color: #ffffff;
                }
                QTabBar::tab:hover {
                    background-color: #8095ab;
                    color: white;
                }
            """)
        
        # propagate to child tabs
        if hasattr(self.performance_tab, 'update_theme'):
            self.performance_tab.update_theme(is_dark)
        if hasattr(self.seo_api_tab, 'update_theme'):
            self.seo_api_tab.update_theme(is_dark)
