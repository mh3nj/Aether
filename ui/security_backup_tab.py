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

        
        self.tabs.addTab(self.security_tab, "\uf3ed Security")
        self.tabs.addTab(self.backup_tab, "\uf019 Backup & Restore")
        
        layout.addWidget(self.tabs)
    
    def update_theme(self, is_dark):
        if is_dark:
            self.tabs.setStyleSheet("""

                QTabWidget::pane {
                    background-color: #1e1f22;
                    border: 1px solid #3e4045;
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
        
        for tab in [self.security_tab, self.backup_tab]:
            if hasattr(tab, 'update_theme'):
                tab.update_theme(is_dark)
