"""
Schema & Social – Merged schema and social media tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.schema_tab import SchemaTab
from ui.og_preview_tab import OGPreviewTab
from ui.breadcrumb_tab import BreadcrumbTab


class SchemaSocialTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.schema_tab = SchemaTab()
        self.og_tab = OGPreviewTab()
        self.breadcrumb_tab = BreadcrumbTab()
        
        self.tabs.addTab(self.schema_tab, "\f201 Schema Library")
        self.tabs.addTab(self.og_tab, "\f3ce OG Preview")
        self.tabs.addTab(self.breadcrumb_tab, "\f0e0 Breadcrumb Builder")
        
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
        
        for tab in [self.schema_tab, self.og_tab, self.breadcrumb_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
