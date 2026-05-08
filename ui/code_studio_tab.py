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
        
        self.formatter_tab = FormatterTab(self.parent_window)
        self.css_tab = CSSOptimizerTab()
        
        self.tabs.addTab(self.formatter_tab, "📝 Code Formatter")
        self.tabs.addTab(self.css_tab, "🎨 CSS Optimizer")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
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
        
        # Propagate to child tabs
        if hasattr(self.formatter_tab, 'update_theme'):
            self.formatter_tab.update_theme(is_dark)
        if hasattr(self.css_tab, 'update_theme'):
            self.css_tab.update_theme(is_dark)
