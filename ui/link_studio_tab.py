"""
Link Studio – Merged link management tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.link_manager import LinkManagerTab
from ui.link_checker_tab import LinkCheckerTab
from ui.internal_links_tab import InternalLinksTab


class LinkStudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.link_manager_tab = LinkManagerTab()
        self.link_checker_tab = LinkCheckerTab()
        self.internal_links_tab = InternalLinksTab()
        
        self.tabs.addTab(self.link_manager_tab, "🔗 Link Manager")
        self.tabs.addTab(self.link_checker_tab, "🔍 Link Checker")
        self.tabs.addTab(self.internal_links_tab, "🔗 Internal Links")
        
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
        
        for tab in [self.link_manager_tab, self.link_checker_tab, self.internal_links_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
