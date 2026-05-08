"""
SEO Command Center – Merged SEO tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.seo_tab import SEOTab
from ui.seo_score_tab import SEOScoreTab
from ui.duplicate_detector_tab import DuplicateDetectorTab
from ui.meta_refresh_tab import MetaRefreshTab


class SEOCommandTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.seo_tab = SEOTab()
        self.score_tab = SEOScoreTab()
        self.duplicate_tab = DuplicateDetectorTab()
        self.meta_refresh_tab = MetaRefreshTab()
        
        self.tabs.addTab(self.seo_tab, "🔍 SEO Optimizer")
        self.tabs.addTab(self.score_tab, "📈 SEO Score")
        self.tabs.addTab(self.duplicate_tab, "🔄 Duplicate Detector")
        self.tabs.addTab(self.meta_refresh_tab, "🔄 Meta Refresh")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.seo_tab, self.score_tab, self.duplicate_tab, self.meta_refresh_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
