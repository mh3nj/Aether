"""
Performance Lab – Merged performance tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.performance_tab import PerformanceTab
from ui.seo_api_tab import SEOAPITab


class PerformanceLabTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.performance_tab = PerformanceTab()
        self.seo_api_tab = SEOAPITab()
        
        self.tabs.addTab(self.performance_tab, "⚡ Preload Scanner")
        self.tabs.addTab(self.seo_api_tab, "🌐 PageSpeed Insights")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.performance_tab, self.seo_api_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
