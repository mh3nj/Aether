"""
Aether Sidebar Navigation – Collapsible sidebar with FontAwesome icons
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont, QIcon


class SidebarButton(QPushButton):
    """Custom sidebar button with FontAwesome icon and text"""
    
    def __init__(self, icon_code, text, shortcut="", parent=None):
        super().__init__(parent)
        self.icon_code = icon_code
        self.text = text
        # Use FontAwesome icon instead of emoji
        self.setText(f"  {icon_code}  {text}")
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
                font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
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
        self.toggle_btn = QPushButton("\uf053  Collapse")  # fa-chevron-left
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
                font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
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
        
        # Navigation buttons with FontAwesome icons
        self.nav_buttons = []
        self.nav_items = [
            ("\uf015", "Dashboard", "Ctrl+1", 0),      # fa-home
            ("\uf121", "Code Studio", "Ctrl+2", 1),    # fa-code
            ("\uf002", "SEO Command", "Ctrl+3", 2),    # fa-search
            ("\uf0e8", "Schema & Social", "Ctrl+4", 3), # fa-share-alt
            ("\uf302", "Media Studio", "Ctrl+5", 4),   # fa-image
            ("\uf0c1", "Link Studio", "Ctrl+6", 5),    # fa-link
            ("\uf29a", "Accessibility Hub", "Ctrl+7", 6), # fa-universal-access
            ("\uf3fd", "Performance Lab", "Ctrl+8", 7), # fa-gauge-high
            ("\uf3ed", "Security & Backup", "Ctrl+9", 8), # fa-shield
            ("\uf080", "Analytics", "Ctrl+0", 9),      # fa-chart-line
            ("\uf013", "Batch Ops", "Ctrl+B", 10),     # fa-gear
            ("\uf017", "Logs", "Ctrl+L", 11),          # fa-clock
        ]
        
        for icon_code, text, shortcut, tab_index in self.nav_items:
            btn = SidebarButton(icon_code, text, shortcut, self)
            btn.clicked.connect(lambda checked, idx=tab_index: self.go_to_tab(idx))
            scroll_layout.insertWidget(scroll_layout.count() - 1, btn)
            self.nav_buttons.append(btn)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Theme toggle at bottom
        self.theme_btn = SidebarButton("\uf186", "Toggle Theme", "Ctrl+Shift+T")  # fa-moon
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)
    
    def go_to_tab(self, index):
        """Switch to tab by index"""
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(index)
            self.update_active_button(index)
    
    def update_active_button(self, active_index):
        """Highlight the active button"""
        is_dark = False
        if self.main_window and hasattr(self.main_window, 'theme_action'):
            is_dark = self.main_window.theme_action.isChecked()
        
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
                        font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
                    }
                    QPushButton:hover {
                        background-color: #8095AB;
                        color: white;
                    }
                """)
            else:
                if is_dark:
                    btn.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding: 8px 12px;
                            border: none;
                            border-radius: 6px;
                            margin: 2px 8px;
                            font-size: 13px;
                            color: #E8E8E8;
                            font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
                        }
                        QPushButton:hover {
                            background-color: rgba(128, 149, 171, 0.2);
                            color: #FFFFFF;
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
                            color: #2C3E50;
                            font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
                        }
                        QPushButton:hover {
                            background-color: rgba(128, 149, 171, 0.2);
                            color: #1A1A2E;
                        }
                    """)
    
    def toggle_theme(self):
        """Toggle dark/light theme"""
        if self.main_window:
            is_dark = self.main_window.theme_action.isChecked()
            self.main_window.theme_action.setChecked(not is_dark)
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
            
            self.toggle_btn.setText("\uf054")  # fa-chevron-right
            
            # Hide text on buttons
            for btn in self.nav_buttons:
                btn.setText(f"  {btn.icon_code}  ")
            self.theme_btn.setText("  \uf186  ")
            
        else:
            # Expand
            self.animation = QPropertyAnimation(self, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(50)
            self.animation.setEndValue(200)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)
            self.animation.start()
            
            self.toggle_btn.setText("\uf053  Collapse")  # fa-chevron-left
            
            # Restore text on buttons
            for i, btn in enumerate(self.nav_buttons):
                if i < len(self.nav_items):
                    icon_code, text, shortcut, tab_index = self.nav_items[i]
                    btn.setText(f"  {icon_code}  {text}")
            self.theme_btn.setText("  \uf186  Toggle Theme")
    
    def update_theme(self, is_dark):
        """Update sidebar theme - called on initialization and theme change"""
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: #1E1F22;
                    border-right: 1px solid #3E4045;
                }
                QPushButton {
                    color: #E8E8E8;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F8F9FA;
                    border-right: 1px solid #D0D7DE;
                }
                QPushButton {
                    color: #2C3E50;
                }
            """)
        # Refresh active button style to apply new text colors
        if self.main_window:
            self.update_active_button(self.main_window.tabs.currentIndex())
