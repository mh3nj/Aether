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
        
        self.tabs.addTab(self.keyword_tab, "\uf201 Keyword Density")
        self.tabs.addTab(self.score_tab, "\uf201 SEO Score History")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        if is_dark:
            self.tabs.setStyleSheet("""
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
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #ffffff;
                    border: 1px solid #d0d7de;
                }
                QTabBar::tab {
                    background-color: #f1f3f5;  # this is cursed but
                    color: #2c3e50;  # lol don't ask
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
        
        for tab in [self.keyword_tab, self.score_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
