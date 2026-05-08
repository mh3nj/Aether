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
)
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtCore import QSettings

# Import all tabs
from ui.dashboard_tab import DashboardTab
from ui.formatter_tab import FormatterTab
from ui.seo_tab import SEOTab
from ui.favicon_tab import FaviconTab
from ui.breadcrumb_tab import BreadcrumbTab
from ui.robots_tab import RobotsTab
from ui.webp_tab import WebPTab
from ui.link_manager import LinkManagerTab
from ui.schema_tab import SchemaTab
from ui.lazy_load_tab import LazyLoadTab
from ui.og_preview_tab import OGPreviewTab
from ui.image_hints_tab import ImageHintsTab
from ui.link_checker_tab import LinkCheckerTab
from ui.accessibility_tab import AccessibilityTab
from ui.alt_checker_tab import AltCheckerTab
from ui.css_optimizer_tab import CSSOptimizerTab
from ui.backup_tab import BackupTab
from ui.seo_score_tab import SEOScoreTab
from ui.duplicate_detector_tab import DuplicateDetectorTab
from ui.security_tab import SecurityTab
from ui.performance_tab import PerformanceTab
from ui.seo_api_tab import SEOAPITab
from ui.meta_refresh_tab import MetaRefreshTab
from ui.serp_preview import SERPPreviewTab
from ui.spell_checker_tab import SpellCheckerTab
from ui.keyword_density_tab import KeywordDensityTab
from ui.internal_links_tab import InternalLinksTab
from ui.content_length_tab import ContentLengthTab
from ui.batch_meta_updater import BatchMetaUpdaterTab
from ui.project_setup_wizard import ProjectSetupWizard, ProjectConfig
from ui.undo_manager import UndoManager
from ui.logs_tab import LogsTab

# Import About Dialog
from ui.about_dialog import AboutDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aether | Web Dev Tools")
        self.setGeometry(100, 100, 1400, 900)

        # Store references to all tabs for theme updates
        self.all_tabs = []

        # Project configuration
        self.project_config = None

        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Settings
        self.settings = QSettings("WebDevTools", "Preferences")

        # Initialize Undo Manager
        self.undo_manager = UndoManager(self)

        # Create dashboard tab FIRST
        self.dashboard_tab = DashboardTab(self, self)
        
        # Create all other tabs
        self.formatter_tab = FormatterTab(self)
        self.seo_tab = SEOTab()
        self.favicon_tab = FaviconTab()
        self.breadcrumb_tab = BreadcrumbTab()
        self.robots_tab = RobotsTab()
        self.webp_tab = WebPTab()
        self.link_manager_tab = LinkManagerTab()
        self.schema_tab = SchemaTab()
        self.lazy_load_tab = LazyLoadTab()
        self.og_preview_tab = OGPreviewTab()
        self.image_hints_tab = ImageHintsTab()
        self.link_checker_tab = LinkCheckerTab()
        self.accessibility_tab = AccessibilityTab()
        self.alt_checker_tab = AltCheckerTab()
        self.css_optimizer_tab = CSSOptimizerTab()
        self.backup_tab = BackupTab()
        self.seo_score_tab = SEOScoreTab()
        self.duplicate_tab = DuplicateDetectorTab()
        self.security_tab = SecurityTab()
        self.performance_tab = PerformanceTab()
        self.seo_api_tab = SEOAPITab()
        self.meta_refresh_tab = MetaRefreshTab()
        self.serp_preview_tab = SERPPreviewTab()
        self.spell_checker_tab = SpellCheckerTab()
        self.keyword_density_tab = KeywordDensityTab()
        self.internal_links_tab = InternalLinksTab()
        self.content_length_tab = ContentLengthTab()
        self.batch_meta_tab = BatchMetaUpdaterTab()
        self.logs_tab = LogsTab(self, self.undo_manager)

        # Add all tabs to the list for theme updates
        self.all_tabs = [
            self.dashboard_tab,
            self.formatter_tab,
            self.seo_tab,
            self.favicon_tab,
            self.breadcrumb_tab,
            self.robots_tab,
            self.webp_tab,
            self.link_manager_tab,
            self.schema_tab,
            self.lazy_load_tab,
            self.og_preview_tab,
            self.image_hints_tab,
            self.link_checker_tab,
            self.accessibility_tab,
            self.alt_checker_tab,
            self.css_optimizer_tab,
            self.backup_tab,
            self.seo_score_tab,
            self.duplicate_tab,
            self.security_tab,
            self.performance_tab,
            self.seo_api_tab,
            self.meta_refresh_tab,
            self.serp_preview_tab,
            self.spell_checker_tab,
            self.keyword_density_tab,
            self.internal_links_tab,
            self.content_length_tab,
            self.batch_meta_tab,
            self.logs_tab
        ]

        # Add tabs to the widget (Dashboard FIRST)
        self.tabs.addTab(self.dashboard_tab, "🏠 Dashboard")
        self.tabs.addTab(self.formatter_tab, "📝 Code Formatter")
        self.tabs.addTab(self.seo_tab, "🔍 SEO Optimizer")
        self.tabs.addTab(self.favicon_tab, "🎨 Favicon Generator")
        self.tabs.addTab(self.breadcrumb_tab, "🧾 Breadcrumb Builder")
        self.tabs.addTab(self.robots_tab, "🤖 Robots & Sitemap")
        self.tabs.addTab(self.webp_tab, "🖼️ WebP Converter")
        self.tabs.addTab(self.link_manager_tab, "🔗 Link Manager")
        self.tabs.addTab(self.schema_tab, "📊 Schema Library")
        self.tabs.addTab(self.lazy_load_tab, "🌸 Smart Lazy Load")
        self.tabs.addTab(self.og_preview_tab, "📱 OG Preview")
        self.tabs.addTab(self.image_hints_tab, "📐 Image Hints")
        self.tabs.addTab(self.link_checker_tab, "🔍 Link Checker")
        self.tabs.addTab(self.accessibility_tab, "♿ Accessibility")
        self.tabs.addTab(self.alt_checker_tab, "🏷️ Alt Checker")
        self.tabs.addTab(self.css_optimizer_tab, "📄 CSS Optimizer")
        self.tabs.addTab(self.backup_tab, "💾 Backup & Restore")
        self.tabs.addTab(self.seo_score_tab, "📈 SEO Score")
        self.tabs.addTab(self.duplicate_tab, "🔄 Duplicate Detector")
        self.tabs.addTab(self.security_tab, "🛡️ Security")
        self.tabs.addTab(self.performance_tab, "⚡ Performance")
        self.tabs.addTab(self.seo_api_tab, "🌐 SEO API")
        self.tabs.addTab(self.meta_refresh_tab, "🔄 Meta Refresh")
        self.tabs.addTab(self.serp_preview_tab, "🔍 SERP Preview")
        self.tabs.addTab(self.spell_checker_tab, "📝 Spell Checker")
        self.tabs.addTab(self.keyword_density_tab, "📊 Keyword Density")
        self.tabs.addTab(self.internal_links_tab, "🔗 Internal Links")
        self.tabs.addTab(self.content_length_tab, "📏 Content Length")
        self.tabs.addTab(self.batch_meta_tab, "⚡ Batch Meta")
        self.tabs.addTab(self.logs_tab, "📋 Logs")

        # Connect logs to dashboard
        self.logs_tab.log_added.connect(self.dashboard_tab.add_log_entry)

        # Tooltips
        tooltips = {
            0: "🏠 Dashboard – Overview and quick actions",
            1: "Format Python, JS, HTML, CSS, TS, JSX files with diff view",
            2: "Edit meta tags, generate hreflang, 404 presets",
            3: "Generate all favicon sizes and inject into HTML",
            4: "Auto-generate BreadcrumbList JSON-LD from URL",
            5: "Create robots.txt and sitemap.xml",
            6: "Convert images to WebP and update HTML",
            7: "Bulk find/replace links across all files",
            8: "Generate FAQ, Product, Article, Event, Recipe, HowTo schema",
            9: "Smart lazy loading with blur-up WebP previews",
            10: "Social media preview (Facebook, Twitter) with injection",
            11: "Detect missing width/height, oversized images",
            12: "Find broken internal and external links",
            13: "Check alt text, lang, headings, labels",
            14: "Bulk fix missing alt attributes",
            15: "Generate print and speech CSS, semantic HTML",
            16: "Create backups and restore previous versions",
            17: "Analyze SEO score (0-100) for each page",
            18: "Find duplicate titles, descriptions, H1 tags",
            19: "CSP & SRI security headers",
            20: "Preload scanner and injector",
            21: "PageSpeed Insights & Core Web Vitals",
            22: "Detect meta refresh redirects",
            23: "Google SERP preview simulator",
            24: "Spelling and grammar checker",
            25: "Keyword density analyzer",
            26: "Internal link suggestions",
            27: "Content length analyzer",
            28: "Batch meta tag updater",
            29: "Complete operation history"
        }
        for idx, tip in tooltips.items():
            if idx < self.tabs.count():
                self.tabs.setTabToolTip(idx, tip)

        # Create menu bar
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")

        self.theme_action = QAction("Toggle Dark Mode", self, checkable=True)
        self.theme_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)

        # Edit menu for Undo/Redo
        edit_menu = menubar.addMenu("Edit")
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        # Project menu
        project_menu = menubar.addMenu("Project")
        setup_project_action = QAction("⚙️ Project Setup Wizard", self)
        setup_project_action.triggered.connect(self.run_project_setup)
        project_menu.addAction(setup_project_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About Aether", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Create toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Project status button
        self.project_status_btn = QPushButton("📁 No Project")
        self.project_status_btn.clicked.connect(self.run_project_setup)
        toolbar.addWidget(self.project_status_btn)
        
        toolbar.addSeparator()
        
        # Undo/Redo toolbar buttons
        self.undo_btn = QPushButton("↩️ Undo")
        self.undo_btn.clicked.connect(self.undo)
        self.undo_btn.setEnabled(False)
        toolbar.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton("↪️ Redo")
        self.redo_btn.clicked.connect(self.redo)
        self.redo_btn.setEnabled(False)
        toolbar.addWidget(self.redo_btn)
        
        toolbar.addSeparator()
        
        self.theme_button = QPushButton("🌓 Toggle Theme")
        self.theme_button.setCheckable(True)
        self.theme_button.clicked.connect(self.on_theme_button_clicked)
        toolbar.addWidget(self.theme_button)

        # Connect undo manager signals
        self.undo_manager.undo_available_changed.connect(self.update_undo_ui)
        self.undo_manager.redo_available_changed.connect(self.update_redo_ui)

        # Add Dashboard shortcut (Ctrl+1)
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.setShortcut(QKeySequence("Ctrl+1"))
        dashboard_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        self.addAction(dashboard_action)

        # Load saved theme preference
        is_dark = self.settings.value("dark_mode", False, type=bool)
        self._set_theme_state(is_dark)

        # Load project configuration
        self.load_project_config()

        self.statusBar().showMessage("Ready - 29 powerful tools at your fingertips | Ctrl+1 for Dashboard")

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
                self.project_status_btn.setText(f"📁 {Path(last_project).name}")
                # Set undo manager project root
                self.undo_manager.set_project_root(last_project)
                self.statusBar().showMessage(f"Project loaded: {last_project}")
                return True
        return False

    def run_project_setup(self):
        """Run the project setup wizard"""
        wizard = ProjectSetupWizard(self)
        if wizard.exec():
            self.project_config = wizard.get_config()
            self.settings.setValue("last_project", self.project_config.root_path)
            project_name = Path(self.project_config.root_path).name
            self.project_status_btn.setText(f"📁 {project_name}")
            # Set undo manager project root
            self.undo_manager.set_project_root(self.project_config.root_path)
            self.statusBar().showMessage(f"Project configured: {self.project_config.root_path}")
            return True
        return False

    def undo(self):
        """Perform undo operation"""
        if self.undo_manager.undo():
            self.statusBar().showMessage("✓ Undo completed", 3000)
            # Refresh current tab if it has refresh method
            current_tab = self.tabs.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
        else:
            self.statusBar().showMessage("Nothing to undo", 2000)

    def redo(self):
        """Perform redo operation"""
        if self.undo_manager.redo():
            self.statusBar().showMessage("✓ Redo completed", 3000)
            current_tab = self.tabs.currentWidget()
            if hasattr(current_tab, 'refresh'):
                current_tab.refresh()
        else:
            self.statusBar().showMessage("Nothing to redo", 2000)

    def update_undo_ui(self, available):
        """Update undo button state"""
        self.undo_action.setEnabled(available)
        self.undo_btn.setEnabled(available)
        if available:
            self.undo_action.setText(self.undo_manager.get_undo_text())
            self.undo_btn.setToolTip(self.undo_manager.get_undo_text())
        else:
            self.undo_action.setText("Undo")
            self.undo_btn.setToolTip("Undo")

    def update_redo_ui(self, available):
        """Update redo button state"""
        self.redo_action.setEnabled(available)
        self.redo_btn.setEnabled(available)
        if available:
            self.redo_action.setText(self.undo_manager.get_redo_text())
            self.redo_btn.setToolTip(self.undo_manager.get_redo_text())
        else:
            self.redo_action.setText("Redo")
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
        is_dark = self.theme_action.isChecked()
        self.theme_button.setChecked(is_dark)
        self._set_theme_state(is_dark)

    def _set_theme_state(self, is_dark):
        """Apply theme and save preference."""
        self.apply_theme(is_dark)
        self.settings.setValue("dark_mode", is_dark)
        self.set_window_logo(is_dark)
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
                background-color: #2B2D31;
                border: 1px solid #3E4045;
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
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #8095AB;
                color: #1E1F22;
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
                background-color: #2B2D31;
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
            """
        else:
            style = """
            QMainWindow, QDialog {
                background-color: #F8F9FA;
            }
            QTabWidget::pane {
                background-color: #FFFFFF;
                border: 1px solid #D0D7DE;
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
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #8095AB;
                color: white;
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
                background-color: #FFFFFF;
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
