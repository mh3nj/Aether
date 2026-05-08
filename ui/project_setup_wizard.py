"""
Aether Project Setup Wizard
One-time configuration for project structure
"""

import json
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem,
    QCheckBox, QGroupBox, QMessageBox, QLineEdit, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


class ScannerThread(QThread):
    """Background thread for scanning project structure"""
    progress = Signal(int)
    found_html = Signal(list)
    found_css = Signal(list)
    found_js = Signal(list)
    found_lang_folders = Signal(list)
    finished = Signal()
    
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        
    def run(self):
        root = Path(self.root_path)
        
        html_files = []
        css_files = []
        js_files = []
        lang_folders = set()
        
        # Scan all files
        all_files = list(root.rglob("*"))
        total = len(all_files)
        
        for idx, file_path in enumerate(all_files):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext in ['.html', '.htm']:
                    html_files.append(str(file_path.relative_to(root)))
                elif ext == '.css':
                    css_files.append(str(file_path.relative_to(root)))
                elif ext == '.js':
                    js_files.append(str(file_path.relative_to(root)))
                
                # Detect language folders (common patterns)
                parts = file_path.parts
                if len(parts) > 1:
                    parent = parts[0]
                    if parent in ['en', 'fa', 'fr', 'de', 'es', 'ar', 'ru', 'zh', 'ja', 'ko']:
                        lang_folders.add(parent)
                    elif parent.endswith('-en') or parent.endswith('-fa'):
                        lang_folders.add(parent)
            
            self.progress.emit(int((idx + 1) / total * 100))
        
        self.found_html.emit(html_files[:50])  # Limit for display
        self.found_css.emit(css_files[:50])
        self.found_js.emit(js_files[:50])
        self.found_lang_folders.emit(sorted(list(lang_folders)))
        self.finished.emit()


class ProjectConfig:
    """Store project configuration"""
    def __init__(self, root_path=""):
        self.root_path = root_path
        self.is_multilingual = False
        self.language_folders = []
        self.html_files = []
        self.css_files = []
        self.js_files = []
        self.main_html = ""
        self.main_css = ""
        self.main_js = ""
        
    def save(self, config_path):
        """Save configuration to JSON file"""
        data = {
            "root_path": self.root_path,
            "is_multilingual": self.is_multilingual,
            "language_folders": self.language_folders,
            "html_files": self.html_files,
            "css_files": self.css_files,
            "js_files": self.js_files,
            "main_html": self.main_html,
            "main_css": self.main_css,
            "main_js": self.main_js,
            "version": "1.0"
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, config_path):
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.root_path = data.get("root_path", "")
        self.is_multilingual = data.get("is_multilingual", False)
        self.language_folders = data.get("language_folders", [])
        self.html_files = data.get("html_files", [])
        self.css_files = data.get("css_files", [])
        self.js_files = data.get("js_files", [])
        self.main_html = data.get("main_html", "")
        self.main_css = data.get("main_css", "")
        self.main_js = data.get("main_js", "")
        return True


class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to Aether")
        
        layout = QVBoxLayout()
        
        welcome_text = QLabel(
            "\uf121 Welcome to Aether Project Setup\n\n"
            "This wizard will help you configure your project for optimal SEO and development tools.\n\n"
            "You'll be asked to:\n"
            "• Select your project folder\n"
            "• Identify language structure (if multi-lingual)\n"
            "• Select main HTML, CSS, and JavaScript files\n\n"
            "This setup only needs to be done once per project.\n"
            "Your configuration will be saved for future sessions."
        )
        welcome_text.setWordWrap(True)
        welcome_text.setFont(QFont("", 11))
        
        layout.addWidget(welcome_text)
        layout.addStretch()
        
        self.setLayout(layout)


class FolderSelectPage(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Select Project Folder")
        self.setSubTitle("Choose the root directory of your website project")
        
        layout = QVBoxLayout()
        
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("padding: 10px; border: 1px solid #8095AB; border-radius: 5px;")
        
        self.select_btn = QPushButton("\uf07c Browse...")
        self.select_btn.clicked.connect(self.select_folder)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.select_btn)
        btn_layout.addStretch()
        
        layout.addWidget(self.folder_label)
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.folder_label.setText(path)
            self.wizard.config.root_path = path
            self.completeChanged.emit()
    
    def isComplete(self):
        return bool(self.wizard.config.root_path)


class ScanProgressPage(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Scanning Project")
        self.setSubTitle("Please wait while Aether analyzes your project structure")
        
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.scan_status = QLabel("Starting scan...")
        self.scan_status.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.scan_status)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.scan_complete = False
        self.scanner = None
    
    def initializePage(self):
        self.scan_complete = False
        self.progress_bar.setValue(0)
        self.scan_status.setText("Scanning files...")
        
        # Start scanner in background
        self.scanner = ScannerThread(self.wizard.config.root_path)
        self.scanner.progress.connect(self.update_progress)
        self.scanner.found_html.connect(self.on_html_found)
        self.scanner.found_css.connect(self.on_css_found)
        self.scanner.found_js.connect(self.on_js_found)
        self.scanner.found_lang_folders.connect(self.on_lang_folders)
        self.scanner.finished.connect(self.on_scan_finished)
        self.scanner.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
    
    def on_html_found(self, files):
        self.wizard.config.html_files = files
    
    def on_css_found(self, files):
        self.wizard.config.css_files = files
    
    def on_js_found(self, files):
        self.wizard.config.js_files = files
    
    def on_lang_folders(self, folders):
        self.wizard.config.language_folders = folders
    
    def on_scan_finished(self):
        self.scan_complete = True
        self.scan_status.setText(f"✓ Scan complete! Found:\n• {len(self.wizard.config.html_files)} HTML files\n• {len(self.wizard.config.css_files)} CSS files\n• {len(self.wizard.config.js_files)} JS files")
        if self.wizard.config.language_folders:
            self.scan_status.setText(self.scan_status.text() + f"\n• Detected language folders: {', '.join(self.wizard.config.language_folders[:5])}")
        self.completeChanged.emit()
    
    def isComplete(self):
        return self.scan_complete


class LanguagePage(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Language Settings")
        self.setSubTitle("Configure multi-language support if applicable")
        
        layout = QVBoxLayout()
        
        self.multilingual_check = QCheckBox("This project supports multiple languages")
        self.multilingual_check.toggled.connect(self.on_multilingual_toggled)
        layout.addWidget(self.multilingual_check)
        
        self.lang_group = QGroupBox("Language Folders")
        self.lang_group.setEnabled(False)
        lang_layout = QVBoxLayout()
        
        self.lang_list = QListWidget()
        self.lang_list.setSelectionMode(QListWidget.MultiSelection)
        self.lang_list.setMaximumHeight(150)
        lang_layout.addWidget(self.lang_list)
        
        self.add_lang_btn = QPushButton("+ Add Custom Language")
        self.add_lang_btn.clicked.connect(self.add_custom_lang)
        lang_layout.addWidget(self.add_lang_btn)
        
        self.lang_group.setLayout(lang_layout)
        layout.addWidget(self.lang_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        # Populate detected language folders
        self.lang_list.clear()
        for folder in self.wizard.config.language_folders:
            item = QListWidgetItem(f"/{folder}/")
            item.setData(Qt.UserRole, folder)
            self.lang_list.addItem(item)
        
        # Auto-select if exactly one detected
        if len(self.wizard.config.language_folders) > 0:
            self.multilingual_check.setChecked(True)
            for i in range(self.lang_list.count()):
                self.lang_list.item(i).setSelected(True)
    
    def on_multilingual_toggled(self, checked):
        self.lang_group.setEnabled(checked)
        self.wizard.config.is_multilingual = checked
        self.completeChanged.emit()
    
    def add_custom_lang(self):
        from PySide6.QtWidgets import QInputDialog
        lang, ok = QInputDialog.getText(self, "Add Language", "Enter language folder name (e.g., 'fr', 'de', 'es'):")
        if ok and lang:
            item = QListWidgetItem(f"/{lang}/")
            item.setData(Qt.UserRole, lang)
            self.lang_list.addItem(item)
            item.setSelected(True)
    
    def validatePage(self):
        if self.multilingual_check.isChecked():
            selected = []
            for i in range(self.lang_list.count()):
                item = self.lang_list.item(i)
                if item.isSelected():
                    selected.append(item.data(Qt.UserRole))
            self.wizard.config.language_folders = selected
        return True
    
    def isComplete(self):
        if self.multilingual_check.isChecked():
            # Need at least one language selected if multilingual is checked
            for i in range(self.lang_list.count()):
                if self.lang_list.item(i).isSelected():
                    return True
            return False
        return True


class FileSelectionPage(QWizardPage):
    def __init__(self, wizard, file_type, title, subtitle):
        super().__init__()
        self.wizard = wizard
        self.file_type = file_type
        self.setTitle(title)
        self.setSubTitle(subtitle)
        
        layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        # For HTML: allow multiple selection, for CSS/JS: single selection
        if file_type == "html":
            self.file_list.setSelectionMode(QListWidget.MultiSelection)
        else:
            self.file_list.setSelectionMode(QListWidget.SingleSelection)
        
        self.file_list.itemSelectionChanged.connect(self.completeChanged)
        layout.addWidget(self.file_list)
        
        self.add_btn = QPushButton("+ Add Custom File")
        self.add_btn.clicked.connect(self.add_custom_file)
        layout.addWidget(self.add_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        self.file_list.clear()
        files = []
        if self.file_type == "html":
            files = self.wizard.config.html_files
        elif self.file_type == "css":
            files = self.wizard.config.css_files
        else:
            files = self.wizard.config.js_files
        
        for f in files[:100]:  # Show more files
            item = QListWidgetItem(f)
            item.setData(Qt.UserRole, f)
            self.file_list.addItem(item)
            # Auto-select first item for CSS/JS if single selection mode
            if self.file_type != "html" and len(files) == 1:
                item.setSelected(True)
    
    def add_custom_file(self):
        from PySide6.QtWidgets import QInputDialog
        file_path, ok = QInputDialog.getText(self, "Add File", f"Enter path to {self.file_type.upper()} file (relative to project root):")
        if ok and file_path:
            # Check if already exists
            existing = False
            for i in range(self.file_list.count()):
                if self.file_list.item(i).text() == file_path:
                    existing = True
                    break
            if not existing:
                item = QListWidgetItem(file_path)
                item.setData(Qt.UserRole, file_path)
                self.file_list.addItem(item)
                item.setSelected(True)
                # Also add to config list
                if self.file_type == "html":
                    self.wizard.config.html_files.append(file_path)
                elif self.file_type == "css":
                    self.wizard.config.css_files.append(file_path)
                else:
                    self.wizard.config.js_files.append(file_path)
    
    def validatePage(self):
        selected = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.isSelected():
                selected.append(item.data(Qt.UserRole))
        
        if not selected:
            return False
        
        if self.file_type == "html":
            self.wizard.config.html_files = selected
            if selected:
                self.wizard.config.main_html = selected[0]
        elif self.file_type == "css":
            self.wizard.config.css_files = selected
            if selected:
                self.wizard.config.main_css = selected[0]
        else:
            self.wizard.config.js_files = selected
            if selected:
                self.wizard.config.main_js = selected[0]
        
        return True
    
    def isComplete(self):
        # Check if at least one item is selected
        for i in range(self.file_list.count()):
            if self.file_list.item(i).isSelected():
                return True
        return False


class SummaryPage(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.setTitle("Setup Complete")
        self.setSubTitle("Review your configuration")
        
        layout = QVBoxLayout()
        
        self.summary_text = QLabel()
        self.summary_text.setWordWrap(True)
        self.summary_text.setFont(QFont("", 10))
        layout.addWidget(self.summary_text)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        config = self.wizard.config
        summary = f"""
\uf00c Project Configuration Summary

\ue185 Project Root: {config.root_path}

\uf0ac Multi-language: {'Yes' if config.is_multilingual else 'No'}
"""
        if config.is_multilingual:
            summary += f"   Language folders: {', '.join(config.language_folders)}\n"

        summary += f"""
\uf15c HTML Files: {len(config.html_files)} selected
   Main: {config.main_html if config.main_html else 'None'}

\uf53f CSS Files: {len(config.css_files)} selected
   Main: {config.main_css if config.main_css else 'None'}

\uf109 JS Files: {len(config.js_files)} selected
   Main: {config.main_js if config.main_js else 'None'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

\uf0eb Your configuration will be saved to:
   {config.root_path}/.aether-config.json

You can always re-run this wizard from Project menu.
"""
        self.summary_text.setText(summary)
    
    def validatePage(self):
        # Save configuration even if some files weren't selected
        config_path = Path(self.wizard.config.root_path) / ".aether-config.json"
        self.wizard.config.save(config_path)
        
        QMessageBox.information(self, "Setup Complete", 
            "\uf00c Project configuration saved successfully!\n\n"
            "All Aether tools will now use this project structure.\n"
            "You can change settings anytime via Project → Project Setup Wizard.")
        
        return True


class ProjectSetupWizard(QWizard):
    """Main setup wizard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aether - Project Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(700, 500)
        
        self.config = ProjectConfig()
        self.scanner = None
        
        # Add pages (no need to loop through .pages())
        self.addPage(WelcomePage())
        self.addPage(FolderSelectPage(self))
        self.addPage(ScanProgressPage(self))
        self.addPage(LanguagePage(self))
        self.addPage(FileSelectionPage(self, "html", "HTML Files", "Select main HTML file(s)"))
        self.addPage(FileSelectionPage(self, "css", "CSS Files", "Select main CSS file(s)"))
        self.addPage(FileSelectionPage(self, "js", "JavaScript Files", "Select main JS file(s)"))
        self.addPage(SummaryPage(self))
        
        self.setButtonText(QWizard.NextButton, "Next")
        self.setButtonText(QWizard.BackButton, "Back")
        self.setButtonText(QWizard.FinishButton, "Complete Setup")
    
    def get_config(self):
        return self.config
