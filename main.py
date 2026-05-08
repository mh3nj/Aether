#!/usr/bin/env python3
"""
Aether | Web Development Tools – Offline GUI App
Complete toolkit for web developers
"""

import sys
import os
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QMenuBar,
    QMenu,
    QToolBar,
    QPushButton,
    QMessageBox,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtCore import Qt, QSettings

# Import dashboard
from ui.dashboard_tab import DashboardTab

# Import merged tabs
from ui.code_studio_tab import CodeStudioTab
from ui.seo_command_tab import SEOCommandTab
from ui.schema_social_tab import SchemaSocialTab
from ui.media_studio_tab import MediaStudioTab
from ui.link_studio_tab import LinkStudioTab
from ui.accessibility_hub_tab import AccessibilityHubTab
from ui.performance_lab_tab import PerformanceLabTab
from ui.security_backup_tab import SecurityBackupTab
from ui.analytics_tab import AnalyticsTab
from ui.batch_ops_tab import BatchOpsTab
from ui.data_bridge import DataBridge

# Import other core components
from ui.project_setup_wizard import ProjectSetupWizard, ProjectConfig
from ui.undo_manager import UndoManager
from ui.logs_tab import LogsTab
from ui.sidebar import Sidebar

# Import About Dialog
from ui.about_dialog import AboutDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("\uf015 Aether | Web Dev Tools")
        self.setGeometry(100, 100, 1400, 900)

        # Store references to all tabs for theme updates
        self.all_tabs = []

        # Project configuration
        self.project_config = None

        # Settings
        self.settings = QSettings("WebDevTools", "Preferences")

        # Initialize Undo Manager
        self.undo_manager = UndoManager(self)

        # Create central widget with horizontal layout for sidebar
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add sidebar
        self.sidebar = Sidebar(self, self)
        main_layout.addWidget(self.sidebar)

        # Create tab widget (with hidden tab bar)
        self.tabs = QTabWidget()
        self.tabs.tabBar().setHidden(True)
        main_layout.addWidget(self.tabs)

        # Create dashboard tab FIRST
        self.dashboard_tab = DashboardTab(self, self)
        
        # Initialize Data Bridge BEFORE creating tabs that need it
        self.data_bridge = DataBridge()
        
        # Create all merged tabs
        self.code_studio_tab = CodeStudioTab(self)
        self.seo_command_tab = SEOCommandTab()
        self.schema_social_tab = SchemaSocialTab()
        self.media_studio_tab = MediaStudioTab()
        self.link_studio_tab = LinkStudioTab()
        self.accessibility_hub_tab = AccessibilityHubTab()
        self.performance_lab_tab = PerformanceLabTab()
        self.security_backup_tab = SecurityBackupTab()
        self.analytics_tab = AnalyticsTab()
        self.batch_ops_tab = BatchOpsTab()
        self.logs_tab = LogsTab(self, self.undo_manager)

        # Add all tabs to the list for theme updates
        self.all_tabs = [
            self.dashboard_tab,
            self.code_studio_tab,
            self.seo_command_tab,
            self.schema_social_tab,
            self.media_studio_tab,
            self.link_studio_tab,
            self.accessibility_hub_tab,
            self.performance_lab_tab,
            self.security_backup_tab,
            self.analytics_tab,
            self.batch_ops_tab,
            self.logs_tab
        ]

        # Connect data bridge to all tabs that support it
        for tab in self.all_tabs:
            if hasattr(tab, 'set_data_bridge'):
                tab.set_data_bridge(self.data_bridge)

        # Add tabs to the widget (without visible tab bar)
        self.tabs.addTab(self.dashboard_tab, "\uf015 Dashboard")
        self.tabs.addTab(self.code_studio_tab, "\uf121 Code Studio")
        self.tabs.addTab(self.seo_command_tab, "\uf002 SEO Command")
        self.tabs.addTab(self.schema_social_tab, "\uf0e8 Schema & Social")
        self.tabs.addTab(self.media_studio_tab, "\uf302 Media Studio")
        self.tabs.addTab(self.link_studio_tab, "\uf0c1 Link Studio")
        self.tabs.addTab(self.accessibility_hub_tab, "\uf29a Accessibility Hub")
        self.tabs.addTab(self.performance_lab_tab, "\uf3fd Performance Lab")
        self.tabs.addTab(self.security_backup_tab, "\uf3ed Security & Backup")
        self.tabs.addTab(self.analytics_tab, "\uf080 Analytics")
        self.tabs.addTab(self.batch_ops_tab, "\uf013 Batch Ops")
        self.tabs.addTab(self.logs_tab, "\uf017 Logs")

        # Connect tab change signal to update sidebar
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Connect logs to dashboard
        self.logs_tab.log_added.connect(self.dashboard_tab.add_log_entry)

        # Connect data bridge to dashboard
        self.data_bridge.scan_completed.connect(self.dashboard_tab.on_scan_completed)
        self.data_bridge.issue_fixed.connect(self.dashboard_tab.on_issue_fixed)

        # Create menu bar
        menubar = self.menuBar()
        
        # Edit menu for Undo/Redo
        edit_menu = menubar.addMenu("Edit")
        
        self.undo_action = QAction("\uf0e2 Undo", self)  # fa-undo
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("\uf01e Redo", self)  # fa-redo
        self.redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        # View menu
        view_menu = menubar.addMenu("View")

        self.theme_action = QAction("\uf186 Toggle Dark Mode", self, checkable=True)  # fa-moon
        self.theme_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

        # Project menu
        project_menu = menubar.addMenu("Project")
        setup_project_action = QAction("\uf013 Project Setup Wizard", self)  # fa-gear
        setup_project_action.triggered.connect(self.run_project_setup)
        project_menu.addAction(setup_project_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("\uf059 About Aether", self)  # fa-question-circle
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Project status button
        self.project_status_btn = QPushButton("\uf187 No Project")  # fa-hdd
        self.project_status_btn.clicked.connect(self.run_project_setup)
        toolbar.addWidget(self.project_status_btn)
        
        toolbar.addSeparator()
        
        # Undo/Redo toolbar buttons
        self.undo_btn = QPushButton("\uf0e2 Undo")
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        toolbar.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("\uf01e Redo")
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        toolbar.addWidget(self.redo_btn)
        
        toolbar.addSeparator()
        
        self.theme_button = QPushButton("\uf186 Toggle Theme")
        self.theme_button.setCheckable(True)
        self.theme_button.clicked.connect(self.on_theme_button_clicked)
        toolbar.addWidget(self.theme_button)

        # Connect undo manager signals
        self.undo_manager.undo_available_changed.connect(self.update_undo_ui)
        self.undo_manager.redo_available_changed.connect(self.update_redo_ui)

        # Add keyboard shortcuts for all tabs
        self.setup_keyboard_shortcuts()

        # Load saved theme preference
        is_dark = self.settings.value("dark_mode", False, type=bool)
        self._set_theme_state(is_dark)

        # Load project configuration
        self.load_project_config()

        self.statusBar().showMessage("\uf0e7 Ready - 12 powerful merged tools | Ctrl+1 for Dashboard")
                
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for tab navigation"""
        
        # Dashboard shortcut (Ctrl+1)
        dashboard_action = QAction(self)
        dashboard_action.setShortcut(QKeySequence("Ctrl+1"))
        dashboard_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        self.addAction(dashboard_action)
        
        # Other shortcuts
        shortcuts = [
            (Qt.Key_2, 1),   # Code Studio
            (Qt.Key_3, 2),   # SEO Command
            (Qt.Key_4, 3),   # Schema & Social
            (Qt.Key_5, 4),   # Media Studio
            (Qt.Key_6, 5),   # Link Studio
            (Qt.Key_7, 6),   # Accessibility Hub
            (Qt.Key_8, 7),   # Performance Lab
            (Qt.Key_9, 8),   # Security & Backup
            (Qt.Key_0, 9),   # Analytics
            (Qt.Key_B, 10),  # Batch Ops
            (Qt.Key_L, 11),  # Logs
        ]
        
        for key, tab_index in shortcuts:
            action = QAction(self)
            if key == Qt.Key_B:
                action.setShortcut(QKeySequence("Ctrl+B"))
            elif key == Qt.Key_L:
                action.setShortcut(QKeySequence("Ctrl+L"))
            else:
                action.setShortcut(QKeySequence(f"Ctrl+{chr(key).upper()}"))
            action.triggered.connect(lambda checked, idx=tab_index: self.tabs.setCurrentIndex(idx))
            self.addAction(action)

    def set_window_logo(self, is_dark):
        """Set the window icon based on theme"""
        if is_dark:
            logo_path = "assets/logos/aether-mark-dark.png"
        else:
            logo_path = "assets/logos/aether-mark-light.png"
        
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

    def load_project_config(self):
        """Load existing project configuration"""
        if self.project_config is None:
            self.project_config = ProjectConfig()
        
        # Check for config file in last used project
        last_project = self.settings.value("last_project", "")
        if last_project and Path(last_project).exists():
            config_path = Path(last_project) / ".aether-config.json"
            if config_path.exists():
                self.project_config.load(config_path)
                self.project_status_btn.setText(f"\uf187 {Path(last_project).name}")
                self.undo_manager.set_project_root(last_project)
                self.statusBar().showMessage(f"\uf187 Project loaded: {last_project}")
                return True
        return False

    def run_project_setup(self):
        """Run the project setup wizard"""
        wizard = ProjectSetupWizard(self)
        if wizard.exec():
            self.project_config = wizard.get_config()
            self.settings.setValue("last_project", self.project_config.root_path)
            project_name = Path(self.project_config.root_path).name
            self.project_status_btn.setText(f"\uf187 {project_name}")
            self.undo_manager.set_project_root(self.project_config.root_path)
            self.statusBar().showMessage(f"\uf187 Project configured: {self.project_config.root_path}")
            return True
        return False

    def on_tab_changed(self, index):
        """Update sidebar when tab changes"""
        self.sidebar.update_active_button(index)

    def undo(self):
        """Perform undo operation"""
        if self.undo_manager.undo():
            self.statusBar().showMessage("\uf00c Undo completed", 3000)
            current_tab = self.tabs.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
        else:
            self.statusBar().showMessage("\uf071 Nothing to undo", 2000)

    def redo(self):
        """Perform redo operation"""
        if self.undo_manager.redo():
            self.statusBar().showMessage("\uf00c Redo completed", 3000)
            current_tab = self.tabs.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
        else:
            self.statusBar().showMessage("\uf071 Nothing to redo", 2000)

    def update_undo_ui(self, available):
        """Update undo button state"""
        self.undo_action.setEnabled(available)
        self.undo_btn.setEnabled(available)
        if available:
            self.undo_action.setText(f"\uf0e2 {self.undo_manager.get_undo_text()}")
            self.undo_btn.setToolTip(self.undo_manager.get_undo_text())
        else:
            self.undo_action.setText("\uf0e2 Undo")
            self.undo_btn.setToolTip("Undo")

    def update_redo_ui(self, available):
        """Update redo button state"""
        self.redo_action.setEnabled(available)
        self.redo_btn.setEnabled(available)
        if available:
            self.redo_action.setText(f"\uf01e {self.undo_manager.get_redo_text()}")
            self.redo_btn.setToolTip(self.undo_manager.get_redo_text())
        else:
            self.redo_action.setText("\uf01e Redo")
            self.redo_btn.setToolTip("Redo")

    def show_about(self):
        """Show about dialog"""
        is_dark = self.theme_action.isChecked()
        about = AboutDialog(self, is_dark)
        about.exec()

    def on_theme_button_clicked(self):
        """Called when toolbar button is clicked."""
        is_dark = self.theme_button.isChecked()
        self.theme_action.setChecked(is_dark)
        self._set_theme_state(is_dark)

    def toggle_theme(self):
        """Called when menu action or shortcut is used."""
        is_dark = self.theme_action.isChecked() if hasattr(self, 'theme_action') else False
        if hasattr(self, 'theme_button'):
            self.theme_button.setChecked(is_dark)
        self._set_theme_state(is_dark)

    def _set_theme_state(self, is_dark):
        """Apply theme and save preference."""
        self.apply_theme(is_dark)
        self.settings.setValue("dark_mode", is_dark)
        self.set_window_logo(is_dark)
        
        # Update sidebar theme (CRITICAL for initial load)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_theme(is_dark)
        
        # Propagate theme to all tabs that have update_theme method
        for tab in self.all_tabs:
            if hasattr(tab, "update_theme"):
                tab.update_theme(is_dark)

    def apply_theme(self, dark):
        if dark:
            style = """
            QMainWindow, QDialog {
                background-color: #1E1F22;
            }
            
            QTabWidget::pane {
                background-color: #1E1F22;
                border: none;
            }
            
            QTabBar::tab {
                background-color: #2B2D31;
                color: #E8E8E8;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3E4045;
                border-bottom: 2px solid #8095AB;
            }
            QTabBar::tab:hover {
                background-color: #4B4E54;
            }
            
            QTabWidget QTabWidget::pane {
                background-color: #1E1F22;
                border: 1px solid #3E4045;
            }
            
            QTabWidget QTabBar::tab {
                background-color: #2B2D31;
                color: #E8E8E8;
                padding: 6px 12px;
            }
            
            QTabWidget QTabBar::tab:selected {
                background-color: #3E4045;
            }
            
            QPlainTextEdit, QTextEdit, QLineEdit, QComboBox, QTreeView, QTableWidget, QListWidget {
                background-color: #2B2D31;
                color: #E8E8E8;
                border: 1px solid #3E4045;
                selection-background-color: #8095AB;
                selection-color: #FFFFFF;
            }
            
            QHeaderView::section {
                background-color: #2B2D31;
                color: #E8E8E8;
                border: 1px solid #3E4045;
            }
            
            QLabel, QStatusBar, QMenuBar, QMenu {
                color: #E8E8E8;
                background-color: #1E1F22;
            }
            
            QPushButton, QToolButton {
                background-color: #2B2D31;
                color: #E8E8E8;
                border: 1px solid #8095AB;
                padding: 5px 10px;
                border-radius: 4px;
                font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #8095AB;
                color: #1E1F22;
            }
            
            QCheckBox {
                color: #E8E8E8;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            
            QGroupBox {
                color: #E8E8E8;
                border: 1px solid #3E4045;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QScrollArea {
                background-color: #1E1F22;
                border: none;
            }
            
            QProgressBar {
                background-color: #2B2D31;
                border: 1px solid #3E4045;
                color: #E8E8E8;
            }
            QProgressBar::chunk {
                background-color: #8095AB;
            }
            
            QScrollBar:vertical {
                background-color: #2B2D31;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #8095AB;
                min-height: 20px;
                border-radius: 6px;
            }
            
            .fas, .far, .fab {
                color: #E8E8E8;
            }
            """
        else:
            style = """
            QMainWindow, QDialog {
                background-color: #F8F9FA;
            }
            
            QTabWidget::pane {
                background-color: #F8F9FA;
                border: none;
            }
            
            QTabBar::tab {
                background-color: #F1F3F5;
                color: #2C3E50;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom: 2px solid #8095AB;
            }
            QTabBar::tab:hover {
                background-color: #8095AB;
                color: white;
            }
            
            QTabWidget QTabWidget::pane {
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
            }
            
            QTabWidget QTabBar::tab {
                background-color: #F1F3F5;
                color: #2C3E50;
            }
            
            QTabWidget QTabBar::tab:selected {
                background-color: #FFFFFF;
            }
            
            QPlainTextEdit, QTextEdit, QLineEdit, QComboBox, QTreeView, QTableWidget, QListWidget {
                background-color: #FFFFFF;
                color: #2C3E50;
                border: 1px solid #D0D7DE;
                selection-background-color: #8095AB;
                selection-color: white;
            }
            
            QHeaderView::section {
                background-color: #F1F3F5;
                color: #2C3E50;
                border: 1px solid #D0D7DE;
            }
            
            QLabel, QStatusBar, QMenuBar, QMenu {
                color: #2C3E50;
                background-color: #F8F9FA;
            }
            
            QPushButton, QToolButton {
                background-color: #E9ECF1;
                color: #2C3E50;
                border: 1px solid #8095AB;
                padding: 5px 10px;
                border-radius: 4px;
                font-family: 'Font Awesome 6 Free', 'Segoe UI', sans-serif;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #8095AB;
                color: white;
            }
            
            QCheckBox {
                color: #2C3E50;
                spacing: 5px;
            }
            
            QGroupBox {
                color: #2C3E50;
                border: 1px solid #D0D7DE;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QScrollArea {
                background-color: #F8F9FA;
                border: none;
            }
            
            QProgressBar {
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
                color: #2C3E50;
            }
            QProgressBar::chunk {
                background-color: #8095AB;
            }
            
            QScrollBar:vertical {
                background-color: #F1F3F5;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background-color: #8095AB;
                min-height: 20px;
                border-radius: 6px;
            }
            
            .fas, .far, .fab {
                color: #2C3E50;
            }
            """
        self.setStyleSheet(style)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Aether")
    app.setOrganizationName("Parsegan")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
