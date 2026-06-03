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
        
        self.tabs.addTab(self.batch_meta_tab, "\uf0e7 Batch Meta Updater")
        self.tabs.addTab(self.robots_tab, "\uf544 Robots & Sitemap")
        
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
                    background-color: #3e4045;  # somebody please refactor this
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
        
        for tab in [self.batch_meta_tab, self.robots_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
