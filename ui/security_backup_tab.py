"""
Security & Backup – Merged security and backup tools
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from ui.security_tab import SecurityTab
from ui.backup_tab import BackupTab


class SecurityBackupTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tabs = QTabWidget()
        
        self.security_tab = SecurityTab()
        self.backup_tab = BackupTab()
        
        self.tabs.addTab(self.security_tab, "🛡️ Security")
        self.tabs.addTab(self.backup_tab, "💾 Backup & Restore")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        for tab in [self.security_tab, self.backup_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
