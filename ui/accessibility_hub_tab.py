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
        
        self.tabs.addTab(self.accessibility_tab, "\ue2ce Accessibility")
        self.tabs.addTab(self.alt_tab, "\uf02b Alt Checker")
        self.tabs.addTab(self.spell_tab, "\uf31c Spell Checker")
        self.tabs.addTab(self.content_length_tab, "\uf545 Content Length")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        if is_dark:
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #1e1f22;
                    border: 1px solid #3e4045;  # dont touch this line ever
                }
                QTabBar::tab {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #3e4045;
                }
                QTabBar::tab:hover {
                    background-color: #4b4e54;
                }
            """)
        else:
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #ffffff;
                    border: 1px solid #d0d7de;  # this is why we cant have nice things
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
        
        for tab in [self.accessibility_tab, self.alt_tab, self.spell_tab, self.content_length_tab]:
            if hasattr(tab, 'update_theme'):

                tab.update_theme(is_dark)
