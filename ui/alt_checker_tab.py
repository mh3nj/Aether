import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QProgressBar, QGroupBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QApplication,
    QLineEdit, QDialog, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class AltFixDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bulk Fix Alt Text")
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.alt_text = QLineEdit()
        self.alt_text.setPlaceholderText("e.g., Image, Decorative, Photo...")
        form.addRow("Default alt text:", self.alt_text)
        
        self.use_filename = QCheckBox("Use filename as alt text (fallback)")
        self.use_filename.setChecked(True)
        form.addRow(self.use_filename)
        
        self.preserve_existing = QCheckBox("Preserve existing alt text (only fix truly missing)")
        self.preserve_existing.setChecked(True)
        form.addRow(self.preserve_existing)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class AltCheckerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for Missing Alt Text")
        self.scan_btn.clicked.connect(self.scan_images)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Image Source", "Current Alt", "Suggested Alt", "Status"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Buttons
        btn_row = QHBoxLayout()
        self.fix_btn = QPushButton("🔧 Bulk Fix Missing Alt Text")
        self.fix_btn.clicked.connect(self.bulk_fix)
        self.fix_btn.setEnabled(False)
        self.preview_btn = QPushButton("👁️ Preview Fixes")
        self.preview_btn.clicked.connect(self.preview_fixes)
        self.preview_btn.setEnabled(False)
        btn_row.addWidget(self.fix_btn)
        btn_row.addWidget(self.preview_btn)
        layout.addLayout(btn_row)

        # Summary
        self.summary_label = QLabel("Ready - Select a folder and click Scan")
        layout.addWidget(self.summary_label)

        self.missing_images = []  # Store for fixing

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def log_msg(self, msg):
        self.summary_label.setText(msg)
        QApplication.processEvents()

    def scan_images(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.log_msg("No HTML files found.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_tree.clear()
        self.missing_images = []

        missing_count = 0

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))

                for img in soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    
                    if not alt or alt.strip() == '':
                        missing_count += 1
                        # Generate suggestion
                        suggested = self.suggest_alt_text(src, img)
                        
                        item = QTreeWidgetItem([
                            rel_path,
                            src[:50],
                            '(empty)' if not alt else alt[:30],
                            suggested,
                            "❌ Missing"
                        ])
                        self.results_tree.addTopLevelItem(item)
                        self.missing_images.append({
                            "file": str(html_path),
                            "rel_path": rel_path,
                            "src": src,
                            "current_alt": alt,
                            "suggested": suggested,
                            "img_tag": img
                        })
                    else:
                        item = QTreeWidgetItem([
                            rel_path,
                            src[:50],
                            alt[:30],
                            "",
                            "✅ OK"
                        ])
                        # Color OK items green
                        for col in range(5):
                            item.setForeground(col, Qt.darkGreen)
                        self.results_tree.addTopLevelItem(item)

            except Exception as e:
                self.log_msg(f"Error: {rel_path} - {str(e)[:50]}")

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if missing_count > 0:
            self.fix_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            self.log_msg(f"⚠️ Found {missing_count} images with missing alt text.")
            QMessageBox.warning(self, "Scan Complete", 
                                f"Found {missing_count} images with missing or empty alt attributes.\n\n"
                                f"Click 'Preview Fixes' to see what will be added.\n"
                                f"Click 'Bulk Fix' to add alt text to all images.")
        else:
            self.fix_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            self.log_msg(f"✅ Great! No missing alt text found in {len(html_files)} files.")

    def suggest_alt_text(self, src, img_tag):
        """Generate intelligent alt text suggestion."""
        # Try from filename
        if src:
            filename = Path(src).stem
            # Clean filename: replace hyphens/underscores with spaces
            suggestion = re.sub(r'[-_]+', ' ', filename)
            suggestion = ' '.join(suggestion.split())
            if suggestion and len(suggestion) > 3:
                return suggestion[:60]
        
        # Try from surrounding text
        parent = img_tag.parent
        if parent:
            surrounding = parent.get_text(strip=True)[:50]
            if surrounding:
                return surrounding[:60]
        
        return "Image (add descriptive alt text)"

    def preview_fixes(self):
        """Show a dialog with all suggested changes."""
        if not self.missing_images:
            QMessageBox.information(self, "Info", "No missing alt text to fix.")
            return
        
        preview_text = "The following alt text will be added:\n\n"
        for img in self.missing_images[:50]:  # Show first 50
            preview_text += f"📁 {img['rel_path']}\n"
            preview_text += f"   🖼️ {img['src'][:60]}\n"
            preview_text += f"   ➡️ alt=\"{img['suggested']}\"\n\n"
        
        if len(self.missing_images) > 50:
            preview_text += f"\n... and {len(self.missing_images) - 50} more images."
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Alt Text Fixes")
        dialog.setMinimumWidth(600)
        layout = QVBoxLayout(dialog)
        text = QLabel(preview_text)
        text.setWordWrap(True)
        layout.addWidget(text)
        
        btn = QPushButton("Close")
        btn.clicked.connect(dialog.accept)
        layout.addWidget(btn)
        
        dialog.exec()

    def bulk_fix(self):
        if not self.missing_images:
            QMessageBox.information(self, "Info", "No missing alt text to fix.")
            return
        
        # Show dialog for options
        dialog = AltFixDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        
        default_alt = dialog.alt_text.text().strip()
        use_filename = dialog.use_filename.isChecked()
        preserve_existing = dialog.preserve_existing.isChecked()
        
        # Count how many will be affected
        to_fix = [img for img in self.missing_images if preserve_existing and not img['current_alt'].strip()] if preserve_existing else self.missing_images
        
        reply = QMessageBox.question(self, "Confirm Bulk Fix", 
                                     f"Add alt text to {len(to_fix)} images?\n\n"
                                     f"Options:\n"
                                     f"• Default alt: '{default_alt}' (if provided)\n"
                                     f"• Use filename: {use_filename}\n"
                                     f"• Preserve existing: {preserve_existing}\n\n"
                                     f"This will modify your HTML files. Continue?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        self.fix_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(to_fix))
        
        fixed_count = 0
        files_modified = set()
        
        for idx, img_data in enumerate(to_fix):
            try:
                # Determine alt text
                if default_alt:
                    new_alt = default_alt
                elif use_filename and img_data['src']:
                    new_alt = self.suggest_alt_text(img_data['src'], None)
                else:
                    new_alt = img_data['suggested']
                
                # Read and modify file
                with open(img_data['file'], 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                # Find the specific img tag
                for img in soup.find_all('img', src=img_data['src']):
                    current_alt = img.get('alt', '')
                    if preserve_existing and current_alt and current_alt.strip():
                        continue
                    img['alt'] = new_alt
                    fixed_count += 1
                
                with open(img_data['file'], 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                files_modified.add(img_data['rel_path'])
                
            except Exception as e:
                self.log_msg(f"Error fixing {img_data['rel_path']}: {str(e)[:50]}")
            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()
        
        self.progress.setVisible(False)
        self.fix_btn.setEnabled(True)
        
        QMessageBox.information(self, "Bulk Fix Complete", 
                                f"Fixed {fixed_count} images with missing alt text.\n"
                                f"Modified {len(files_modified)} files.")
        self.log_msg(f"✅ Fixed {fixed_count} images across {len(files_modified)} files")
        
        # Rescan to refresh display
        self.scan_images()

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    alternate-background-color: #3E4045;
                    background-color: #2B2D31;
                    color: #E8E8E8;
                }
                QHeaderView::section {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
            """)
        else:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    alternate-background-color: #F8F9FA;
                    background-color: #FFFFFF;
                    color: #2C3E50;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
