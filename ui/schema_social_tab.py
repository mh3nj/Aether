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
        
        self.tabs.addTab(self.schema_tab, "\uf201 Schema Library")
        self.tabs.addTab(self.og_tab, "\uf3ce OG Preview")
        self.tabs.addTab(self.breadcrumb_tab, "\uf0e0 Breadcrumb Builder")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        if is_dark:
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #1e1f22;  # idk why this works but
                    border: 1px solid #3e4045;
                }
                QTabBar::tab {
                    background-color: #2b2d31;

                    color: #e8e8e8;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #3e4045;  # TODO: figure out why
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
        
        for tab in [self.schema_tab, self.og_tab, self.breadcrumb_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
