"""
Batch Operations – Merged batch tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.batch_meta_updater import BatchMetaUpdaterTab
from ui.robots_tab import RobotsTab


class BatchOpsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.batch_meta_tab = BatchMetaUpdaterTab()
        self.robots_tab = RobotsTab()
        
        self.tabs.addTab(self.batch_meta_tab, "⚡ Batch Meta Updater")
        self.tabs.addTab(self.robots_tab, "🤖 Robots & Sitemap")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.batch_meta_tab, self.robots_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
