import os
import re
from pathlib import Path
from urllib.parse import urlparse
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QFormLayout, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QSplitter, QTabWidget, QApplication
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class LinkManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.links_data = []  # list of dicts: file, tag, attr, original_link
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Project folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan All Links")
        self.scan_btn.clicked.connect(self.scan_links)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Tabs: Links Table + Bulk Replace
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # === Tab 1: Links Table ===
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        self.links_table = QTableWidget()
        self.links_table.setColumnCount(5)
        self.links_table.setHorizontalHeaderLabels(["File", "Tag", "Attribute", "Original Link", "New Link Preview"])
        self.links_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.links_table.setAlternatingRowColors(True)
        
        # Connect double-click for inline editing
        self.links_table.itemDoubleClicked.connect(self.on_cell_double_clicked)
        
        table_layout.addWidget(self.links_table)
        
        # Filter and action row
        filter_row = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter links...")
        self.filter_edit.textChanged.connect(self.filter_links)
        self.apply_single_btn = QPushButton("✏️ Apply Selected Fix")
        self.apply_single_btn.clicked.connect(self.apply_single_fix)
        filter_row.addWidget(self.filter_edit)
        filter_row.addWidget(self.apply_single_btn)
        table_layout.addLayout(filter_row)
        
        self.tabs.addTab(table_tab, "📋 All Links")

        # === Tab 2: Bulk Replace ===
        replace_tab = QWidget()
        replace_layout = QVBoxLayout(replace_tab)

        replace_group = QGroupBox("Find & Replace")
        replace_form = QFormLayout()
        self.find_text = QLineEdit()
        self.find_text.setPlaceholderText("e.g., https://old-site.com/ or /old-path/")
        replace_form.addRow("Find:", self.find_text)
        self.replace_text = QLineEdit()
        self.replace_text.setPlaceholderText("e.g., https://new-site.com/ or /new-path/")
        replace_form.addRow("Replace with:", self.replace_text)
        self.regex_check = QCheckBox("Use regular expression")
        replace_form.addRow(self.regex_check)
        self.preview_btn = QPushButton("Preview Changes")
        self.preview_btn.clicked.connect(self.preview_replace)
        replace_form.addRow(self.preview_btn)
        replace_group.setLayout(replace_form)
        replace_layout.addWidget(replace_group)

        self.replace_preview = QPlainTextEdit()
        self.replace_preview.setReadOnly(True)
        self.replace_preview.setMaximumHeight(200)
        replace_layout.addWidget(QLabel("Preview of changes (first 10 matches):"))
        replace_layout.addWidget(self.replace_preview)

        self.apply_replace_btn = QPushButton("Apply Replace to All Files")
        self.apply_replace_btn.clicked.connect(self.apply_replace)
        replace_layout.addWidget(self.apply_replace_btn)

        self.tabs.addTab(replace_tab, "🔄 Bulk Replace")

        # Progress and status
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Ready – select a folder and click Scan")
        layout.addWidget(self.status_label)

        self.all_links = []  # unfiltered
        self.filtered_links = []

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)
            self.status_label.setText(f"Project: {path}")

    def scan_links(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("Scanning for links...")
        QApplication.processEvents()

        html_files = list(Path(self.project_folder).rglob("*.html"))
        self.progress.setMaximum(len(html_files))
        self.all_links = []

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = html_path.relative_to(self.project_folder)

                # Find all tags with href or src
                for tag in soup.find_all(['a', 'link', 'script', 'img']):
                    for attr in ['href', 'src']:
                        if tag.has_attr(attr):
                            link = tag[attr]
                            if link and not link.startswith('#') and not link.startswith('javascript:'):
                                self.all_links.append({
                                    'file': str(rel_path),
                                    'tag': tag.name,
                                    'attr': attr,
                                    'original': link,
                                    'full_path': str(html_path),
                                    'new_preview': link,  # Initialize with original
                                })
            except Exception as e:
                pass
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.filtered_links = self.all_links.copy()
        self.update_table()
        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        self.status_label.setText(f"Found {len(self.all_links)} links in {len(html_files)} HTML files.")

    def update_table(self):
        self.links_table.setRowCount(len(self.filtered_links))
        for row, link in enumerate(self.filtered_links):
            self.links_table.setItem(row, 0, QTableWidgetItem(link['file']))
            self.links_table.setItem(row, 1, QTableWidgetItem(link['tag']))
            self.links_table.setItem(row, 2, QTableWidgetItem(link['attr']))
            self.links_table.setItem(row, 3, QTableWidgetItem(link['original']))
            
            # Editable preview column
            preview_value = link.get('new_preview', link['original'])
            preview_item = QTableWidgetItem(preview_value)
            preview_item.setFlags(preview_item.flags() | Qt.ItemIsEditable)
            self.links_table.setItem(row, 4, preview_item)

    def filter_links(self):
        text = self.filter_edit.text().lower()
        if not text:
            self.filtered_links = self.all_links.copy()
        else:
            self.filtered_links = [l for l in self.all_links if text in l['original'].lower() or text in l['file'].lower()]
        self.update_table()

    def preview_replace(self):
        find = self.find_text.text()
        replace = self.replace_text.text()
        if not find:
            QMessageBox.warning(self, "Warning", "Enter text to find.")
            return

        use_regex = self.regex_check.isChecked()
        preview_lines = []
        count = 0
        for link in self.all_links[:50]:  # preview first 50
            old = link['original']
            if use_regex:
                try:
                    new = re.sub(find, replace, old)
                except:
                    new = old
            else:
                new = old.replace(find, replace)
            if new != old:
                preview_lines.append(f"{link['file']}: {old} → {new}")
                count += 1
                if count >= 10:
                    preview_lines.append("... (showing first 10 matches)")
                    break

        if not preview_lines:
            self.replace_preview.setPlainText("No matches found.")
        else:
            self.replace_preview.setPlainText("\n".join(preview_lines))
        self.status_label.setText(f"Preview: {count} matches found.")

    def on_cell_double_clicked(self, item):
        """Allow editing the New Link Preview column"""
        row = item.row()
        column = item.column()
        
        if column == 4:  # New Link Preview column
            current_text = self.links_table.item(row, column).text()
            # Create an inline editor
            from PySide6.QtWidgets import QLineEdit
            editor = QLineEdit(current_text)
            
            # Apply theme-aware style
            is_dark = hasattr(self, 'parent') and self.parent() and hasattr(self.parent(), 'theme_action')
            if is_dark and self.parent().theme_action.isChecked():
                editor.setStyleSheet("background-color: #2B2D31; color: #E8E8E8; border: 1px solid #8095AB;")
            else:
                editor.setStyleSheet("background-color: #FFFFFF; color: #2C3E50; border: 1px solid #8095AB;")
            
            def save_changes():
                new_value = editor.text()
                if new_value != current_text:
                    self.links_table.item(row, column).setText(new_value)
                    # Update the stored link data
                    if row < len(self.filtered_links):
                        self.filtered_links[row]['new_preview'] = new_value
                    self.status_label.setText(f"Updated preview: {new_value}")
                self.links_table.setCellWidget(row, column, None)
            
            editor.returnPressed.connect(save_changes)
            editor.editingFinished.connect(save_changes)
            
            self.links_table.setCellWidget(row, column, editor)
            editor.setFocus()
            editor.selectAll()

    def apply_single_fix(self):
        """Apply the edited link preview to the actual HTML file for selected row"""
        current_row = self.links_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Select a link first.")
            return
        
        if current_row >= len(self.filtered_links):
            return
            
        link_data = self.filtered_links[current_row]
        new_link = self.links_table.item(current_row, 4).text()  # New Link Preview column
        
        if not new_link or new_link == link_data['original']:
            self.status_label.setText("No change to apply.")
            return
        
        # Apply to file
        try:
            with open(link_data['full_path'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace only this specific occurrence
            if link_data['original'] in content:
                new_content = content.replace(link_data['original'], new_link, 1)
                
                with open(link_data['full_path'], 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                # Update the display
                self.links_table.item(current_row, 3).setText(new_link)
                self.links_table.item(current_row, 4).setText("✅ Applied")
                link_data['original'] = new_link  # Update stored value
                self.status_label.setText(f"Link updated in {link_data['file']}")
            else:
                self.status_label.setText("Original link not found in file - already changed?")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update: {e}")

    def apply_replace(self):
        find = self.find_text.text()
        replace = self.replace_text.text()
        if not find:
            QMessageBox.warning(self, "Warning", "Enter text to find.")
            return

        reply = QMessageBox.question(self, "Confirm Replace", 
                                     f"Replace '{find}' with '{replace}' in all HTML files?\nThis cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        use_regex = self.regex_check.isChecked()
        files_modified = set()
        total_replacements = 0

        for link in self.all_links:
            old = link['original']
            if use_regex:
                try:
                    new = re.sub(find, replace, old)
                except:
                    continue
            else:
                new = old.replace(find, replace)
            if new != old:
                # Update the actual HTML file
                file_path = link['full_path']
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Replace in content (simple string replace)
                if use_regex:
                    new_content = re.sub(find, replace, content)
                else:
                    new_content = content.replace(old, new)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                files_modified.add(file_path)
                total_replacements += 1

        self.status_label.setText(f"Applied {total_replacements} replacements in {len(files_modified)} files.")
        QMessageBox.information(self, "Done", f"Replaced {total_replacements} links in {len(files_modified)} files.")
        # Rescan to refresh table
        self.scan_links()

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.links_table.setStyleSheet("""
                QTableWidget {
                    alternate-background-color: #3E4045;
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    gridline-color: #3E4045;
                }
                QHeaderView::section {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
            """)
            self.replace_preview.setStyleSheet("background-color: #2B2D31; color: #E8E8E8;")
        else:
            self.links_table.setStyleSheet("""
                QTableWidget {
                    alternate-background-color: #F8F9FA;
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    gridline-color: #D0D7DE;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
            self.replace_preview.setStyleSheet("background-color: #FFFFFF; color: #2C3E50;")
