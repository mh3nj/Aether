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
        
        self.tabs.addTab(self.accessibility_tab, "♿ Accessibility")
        self.tabs.addTab(self.alt_tab, "🏷️ Alt Checker")
        self.tabs.addTab(self.spell_tab, "📝 Spell Checker")
        self.tabs.addTab(self.content_length_tab, "📏 Content Length")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.accessibility_tab, self.alt_tab, self.spell_tab, self.content_length_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
