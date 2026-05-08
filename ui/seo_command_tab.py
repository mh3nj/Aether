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
        
        self.tabs.addTab(self.seo_tab, "\ue522 SEO Optimizer")
        self.tabs.addTab(self.score_tab, "\uf201 SEO Score")
        self.tabs.addTab(self.duplicate_tab, "\uf1b8 Duplicate Detector")
        self.tabs.addTab(self.meta_refresh_tab, "\uf1b8 Meta Refresh")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        if is_dark:
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #1E1F22;
                    border: 1px solid #3E4045;
                }
                QTabBar::tab {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #3E4045;
                }
                QTabBar::tab:hover {
                    background-color: #4B4E54;
                }
            """)
        else:
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #FFFFFF;
                    border: 1px solid #D0D7DE;
                }
                QTabBar::tab {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #FFFFFF;
                }
                QTabBar::tab:hover {
                    background-color: #8095AB;
                    color: white;
                }
            """)
        
        for tab in [self.seo_tab, self.score_tab, self.duplicate_tab, self.meta_refresh_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
