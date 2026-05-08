"""
Media Studio – Merged image/media tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.favicon_tab import FaviconTab
from ui.webp_tab import WebPTab
from ui.lazy_load_tab import LazyLoadTab
from ui.image_hints_tab import ImageHintsTab


class MediaStudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.favicon_tab = FaviconTab()
        self.webp_tab = WebPTab()
        self.lazy_tab = LazyLoadTab()
        self.image_hints_tab = ImageHintsTab()
        
        self.tabs.addTab(self.favicon_tab, "🎨 Favicon Generator")
        self.tabs.addTab(self.webp_tab, "🖼️ WebP Converter")
        self.tabs.addTab(self.lazy_tab, "🌸 Smart Lazy Load")
        self.tabs.addTab(self.image_hints_tab, "📐 Image Hints")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.favicon_tab, self.webp_tab, self.lazy_tab, self.image_hints_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
