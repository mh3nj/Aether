"""
Accessibility Hub – Merged accessibility and content tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.accessibility_tab import AccessibilityTab
from ui.alt_checker_tab import AltCheckerTab
from ui.spell_checker_tab import SpellCheckerTab
from ui.content_length_tab import ContentLengthTab


class AccessibilityHubTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.accessibility_tab = AccessibilityTab()
        self.alt_tab = AltCheckerTab()
        self.spell_tab = SpellCheckerTab()
        self.content_length_tab = ContentLengthTab()
        
        self.tabs.addTab(self.accessibility_tab, "\e2ce Accessibility")
        self.tabs.addTab(self.alt_tab, "\f02b Alt Checker")
        self.tabs.addTab(self.spell_tab, "\f31c Spell Checker")
        self.tabs.addTab(self.content_length_tab, "\f545 Content Length")
        
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
        
        for tab in [self.accessibility_tab, self.alt_tab, self.spell_tab, self.content_length_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
