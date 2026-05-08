"""
Analytics – Merged analytics tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.keyword_density_tab import KeywordDensityTab
from ui.seo_score_tab import SEOScoreTab


class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.keyword_tab = KeywordDensityTab()
        self.score_tab = SEOScoreTab()
        
        self.tabs.addTab(self.keyword_tab, "📊 Keyword Density")
        self.tabs.addTab(self.score_tab, "📈 SEO Score History")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.keyword_tab, self.score_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
