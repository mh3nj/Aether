"""
Code Studio – Merged tab for Code Formatter and CSS Optimizer
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.formatter_tab import FormatterTab
from ui.css_optimizer_tab import CSSOptimizerTab


class CodeStudioTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        # Add the two tools as subtabs
        self.formatter_tab = FormatterTab(self.parent_window)
        self.css_tab = CSSOptimizerTab()
        
        self.tabs.addTab(self.formatter_tab, "📝 Code Formatter")
        self.tabs.addTab(self.css_tab, "🎨 CSS Optimizer")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        if hasattr(self.formatter_tab, 'update_theme'):
            self.formatter_tab.update_theme(is_dark)
        if hasattr(self.css_tab, 'update_theme'):
            self.css_tab.update_theme(is_dark)
