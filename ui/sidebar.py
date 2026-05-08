"""
Aether Sidebar Navigation – Collapsible sidebar for quick access
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QIcon


class SidebarButton(QPushButton):
    """Custom sidebar button with icon and text"""
    
    def __init__(self, icon, text, shortcut="", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}  {text}")
        if shortcut:
            self.setToolTip(f"{text} ({shortcut})")
        self.setFixedHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: none;
                border-radius: 6px;
                margin: 2px 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(128, 149, 171, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(128, 149, 171, 0.3);
            }
        """)


class Sidebar(QWidget):
    """Collapsible sidebar navigation"""
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.is_collapsed = False
        self.setFixedWidth(200)
        self.setMinimumWidth(50)
        self.setMaximumWidth(200)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(2)
        
        # Collapse/Expand button
        self.toggle_btn = QPushButton("◀ Collapse")
        self.toggle_btn.setFixedHeight(35)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(128, 149, 171, 0.1);
                border: none;
                border-radius: 6px;
                margin: 5px 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(128, 149, 171, 0.2);
            }
        """)
        layout.addWidget(self.toggle_btn)
        
        # Scroll area for buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(2)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.addStretch()
        
        # Navigation buttons
        self.nav_buttons = []
        
        nav_items = [
            ("🏠", "Dashboard", "Ctrl+1", 0),
            ("📝", "Code Studio", "Ctrl+2", 1),
            ("🔍", "SEO Command", "Ctrl+3", 2),
            ("📊", "Schema & Social", "Ctrl+4", 3),
            ("🖼️", "Media Studio", "Ctrl+5", 4),
            ("🔗", "Link Studio", "Ctrl+6", 5),
            ("♿", "Accessibility", "Ctrl+7", 6),
            ("⚡", "Performance Lab", "Ctrl+8", 7),
            ("🛡️", "Security & Backup", "Ctrl+9", 8),
            ("📈", "Analytics", "Ctrl+0", 9),
            ("⚙️", "Batch Ops", "Ctrl+B", 10),
            ("📋", "Logs", "Ctrl+L", 11),
        ]
        
        for icon, text, shortcut, tab_index in nav_items:
            btn = SidebarButton(icon, text, shortcut, self)
            btn.clicked.connect(lambda checked, idx=tab_index: self.go_to_tab(idx))
            scroll_layout.insertWidget(scroll_layout.count() - 1, btn)
            self.nav_buttons.append(btn)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Theme toggle at bottom
        self.theme_btn = SidebarButton("🌓", "Toggle Theme", "Ctrl+Shift+T")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)
    
    def go_to_tab(self, index):
        """Switch to tab by index"""
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(index)
            self.update_active_button(index)
    
    def update_active_button(self, active_index):
        """Highlight the active button"""
        for i, btn in enumerate(self.nav_buttons):
            if i == active_index:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 8px 12px;
                        border: none;
                        border-radius: 6px;
                        margin: 2px 8px;
                        background-color: #8095AB;
                        color: white;
                        font-weight: bold;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 8px 12px;
                        border: none;
                        border-radius: 6px;
                        margin: 2px 8px;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: rgba(128, 149, 171, 0.2);
                    }
                """)
    
    def toggle_theme(self):
        """Toggle dark/light theme"""
        if self.main_window:
            self.main_window.toggle_theme()
    
    def toggle_collapse(self):
        """Collapse or expand the sidebar"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            # Collapse
            self.animation = QPropertyAnimation(self, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(200)
            self.animation.setEndValue(50)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()
            
            self.toggle_btn.setText("▶")
            
            # Hide text on buttons
            for btn in self.nav_buttons:
                btn.setText("  " + btn.text()[0] + "  ")
            self.theme_btn.setText("  🌓  ")
            
        else:
            # Expand
            self.animation = QPropertyAnimation(self, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(50)
            self.animation.setEndValue(200)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()
            
            self.toggle_btn.setText("◀ Collapse")
            
            # Restore text on buttons
            original_texts = [
                ("🏠", "Dashboard"),
                ("📝", "Code Studio"),
                ("🔍", "SEO Command"),
                ("📊", "Schema & Social"),
                ("🖼️", "Media Studio"),
                ("🔗", "Link Studio"),
                ("♿", "Accessibility"),
                ("⚡", "Performance Lab"),
                ("🛡️", "Security & Backup"),
                ("📈", "Analytics"),
                ("⚙️", "Batch Ops"),
                ("📋", "Logs"),
            ]
            for i, btn in enumerate(self.nav_buttons):
                if i < len(original_texts):
                    icon, text = original_texts[i]
                    btn.setText(f"  {icon}  {text}")
            self.theme_btn.setText("  🌓  Toggle Theme")
    
    def update_theme(self, is_dark):
        """Update sidebar theme"""
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1F22;
                    border-right: 1px solid #3E4045;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F8F9FA;
                    border-right: 1px solid #D0D7DE;
                }
            """)
