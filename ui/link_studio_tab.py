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
        for tab in [self.link_manager_tab, self.link_checker_tab, self.internal_links_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
