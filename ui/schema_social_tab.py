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
        
        self.tabs.addTab(self.schema_tab, "📊 Schema Library")
        self.tabs.addTab(self.og_tab, "📱 OG Preview")
        self.tabs.addTab(self.breadcrumb_tab, "🧾 Breadcrumb Builder")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.schema_tab, self.og_tab, self.breadcrumb_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
