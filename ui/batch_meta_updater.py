"""
Aether Batch Meta Tag Updater - Update meta tags across multiple HTML files at once
"""

import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QFormLayout, QLineEdit, QComboBox, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class BatchMetaUpdaterTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.html_files = []
        self.preview_results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for HTML Files")
        self.scan_btn.clicked.connect(self.scan_files)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Meta tag selection
        meta_group = QGroupBox("Meta Tag to Update")
        meta_layout = QFormLayout(meta_group)
        
        self.meta_type = QComboBox()
        self.meta_type.addItems([
            "title", "meta description", "meta robots", 
            "canonical URL", "author", "viewport", 
            "og:title", "og:description", "og:image", "twitter:title", "twitter:description"
        ])
        self.meta_type.currentTextChanged.connect(self.on_meta_type_changed)
        meta_layout.addRow("Select Tag:", self.meta_type)
        
        self.new_value = QTextEdit()
        self.new_value.setMaximumHeight(80)
        self.new_value.setPlaceholderText("Enter new value for the selected meta tag...")
        meta_layout.addRow("New Value:", self.new_value)
        
        self.append_mode = QCheckBox("Append to existing (instead of replace)")
        self.append_mode.setToolTip("If checked, new value will be added after existing content")
        meta_layout.addRow(self.append_mode)
        
        self.append_separator = QLineEdit(" | ")
        self.append_separator.setPlaceholderText("Separator (e.g., ' | ', ' - ')")
        meta_layout.addRow("Separator for append:", self.append_separator)
        
        layout.addWidget(meta_group)

        # Preview button and results
        self.preview_btn = QPushButton("👁️ Preview Changes")
        self.preview_btn.clicked.connect(self.preview_changes)
        self.preview_btn.setEnabled(False)
        layout.addWidget(self.preview_btn)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Current Value", "New Value", "Status"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Apply button
        self.apply_btn = QPushButton("🚀 Apply Changes to All Files")
        self.apply_btn.clicked.connect(self.apply_changes)
        self.apply_btn.setEnabled(False)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #2B2D31;
                color: #E8E8E8;
                border: 1px solid #4CAF50;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4CAF50;
                color: white;
            }
        """)
        layout.addWidget(self.apply_btn)

        self.summary_label = QLabel("Ready - Select a folder, choose a meta tag, enter new value, then Preview")
        layout.addWidget(self.summary_label)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def scan_files(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a folder first.")
            return

        self.html_files = list(Path(self.project_folder).rglob("*.html"))
        if not self.html_files:
            self.summary_label.setText("No HTML files found.")
            return

        self.summary_label.setText(f"Found {len(self.html_files)} HTML files. Select a meta tag and enter new value.")
        self.preview_btn.setEnabled(True)
        QMessageBox.information(self, "Scan Complete", f"Found {len(self.html_files)} HTML files to update.")

    def on_meta_type_changed(self, tag_type):
        """Update placeholder based on selected meta tag"""
        placeholders = {
            "title": "e.g., My New Page Title - Brand Name",
            "meta description": "e.g., This is my new meta description for SEO, between 150-160 characters.",
            "meta robots": "e.g., index, follow  OR  noindex, nofollow",
            "canonical URL": "e.g., https://example.com/preferred-page.html",
            "author": "e.g., John Doe",
            "viewport": "e.g., width=device-width, initial-scale=1.0",
            "og:title": "e.g., My Page Title for Facebook Sharing",
            "og:description": "e.g., This description appears when shared on Facebook",
            "og:image": "e.g., https://example.com/social-image.jpg",
            "twitter:title": "e.g., My Page Title for Twitter",
            "twitter:description": "e.g., This description appears on Twitter cards"
        }
        self.new_value.setPlaceholderText(placeholders.get(tag_type, "Enter new value..."))

    def get_current_value(self, soup, tag_type):
        """Extract current value of the selected meta tag"""
        if tag_type == "title":
            title_tag = soup.find('title')
            return title_tag.string if title_tag and title_tag.string else ""
        
        elif tag_type == "meta description":
            meta = soup.find('meta', attrs={'name': 'description'})
            return meta.get('content', '') if meta else ""
        
        elif tag_type == "meta robots":
            meta = soup.find('meta', attrs={'name': 'robots'})
            return meta.get('content', '') if meta else ""
        
        elif tag_type == "canonical URL":
            link = soup.find('link', attrs={'rel': 'canonical'})
            return link.get('href', '') if link else ""
        
        elif tag_type in ["author", "viewport"]:
            meta = soup.find('meta', attrs={'name': tag_type})
            return meta.get('content', '') if meta else ""
        
        elif tag_type.startswith("og:"):
            meta = soup.find('meta', attrs={'property': tag_type})
            return meta.get('content', '') if meta else ""
        
        elif tag_type.startswith("twitter:"):
            meta = soup.find('meta', attrs={'name': tag_type})
            return meta.get('content', '') if meta else ""
        
        return ""

    def update_value(self, soup, tag_type, new_value, append_mode, separator):
        """Update or create the meta tag with new value"""
        if tag_type == "title":
            title_tag = soup.find('title')
            if title_tag:
                if append_mode and title_tag.string:
                    title_tag.string = title_tag.string + separator + new_value
                else:
                    title_tag.string = new_value
            else:
                new_title = soup.new_tag('title')
                new_title.string = new_value
                head = soup.head or soup.new_tag('head')
                if not soup.head:
                    soup.html.insert(0, head)
                head.append(new_title)
        
        elif tag_type in ["meta description", "meta robots", "author", "viewport"]:
            name = tag_type.replace("meta ", "")
            meta = soup.find('meta', attrs={'name': name})
            if meta:
                current = meta.get('content', '')
                if append_mode and current:
                    meta['content'] = current + separator + new_value
                else:
                    meta['content'] = new_value
            else:
                new_meta = soup.new_tag('meta', name=name, content=new_value)
                head = soup.head or soup.new_tag('head')
                if not soup.head:
                    soup.html.insert(0, head)
                head.append(new_meta)
        
        elif tag_type == "canonical URL":
            link = soup.find('link', attrs={'rel': 'canonical'})
            if link:
                if append_mode and link.get('href'):
                    link['href'] = link['href'] + separator + new_value
                else:
                    link['href'] = new_value
            else:
                new_link = soup.new_tag('link', rel='canonical', href=new_value)
                head = soup.head or soup.new_tag('head')
                if not soup.head:
                    soup.html.insert(0, head)
                head.append(new_link)
        
        elif tag_type.startswith("og:"):
            meta = soup.find('meta', attrs={'property': tag_type})
            if meta:
                current = meta.get('content', '')
                if append_mode and current:
                    meta['content'] = current + separator + new_value
                else:
                    meta['content'] = new_value
            else:
                new_meta = soup.new_tag('meta', property=tag_type, content=new_value)
                head = soup.head or soup.new_tag('head')
                if not soup.head:
                    soup.html.insert(0, head)
                head.append(new_meta)
        
        elif tag_type.startswith("twitter:"):
            meta = soup.find('meta', attrs={'name': tag_type})
            if meta:
                current = meta.get('content', '')
                if append_mode and current:
                    meta['content'] = current + separator + new_value
                else:
                    meta['content'] = new_value
            else:
                new_meta = soup.new_tag('meta', name=tag_type, content=new_value)
                head = soup.head or soup.new_tag('head')
                if not soup.head:
                    soup.html.insert(0, head)
                head.append(new_meta)

    def preview_changes(self):
        if not self.html_files:
            QMessageBox.warning(self, "Warning", "No HTML files. Click Scan first.")
            return
        
        new_value = self.new_value.toPlainText().strip()
        if not new_value:
            QMessageBox.warning(self, "Warning", "Enter a new value for the meta tag.")
            return

        self.results_tree.clear()
        self.preview_results = []
        
        tag_type = self.meta_type.currentText()
        append_mode = self.append_mode.isChecked()
        separator = self.append_separator.text()
        
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.html_files))
        
        for idx, html_path in enumerate(self.html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                current_value = self.get_current_value(soup, tag_type)
                rel_path = str(html_path.relative_to(self.project_folder))
                
                if append_mode and current_value:
                    new_display = current_value + separator + new_value
                else:
                    new_display = new_value
                
                item = QTreeWidgetItem([rel_path, current_value[:80], new_display[:80], "Pending"])
                if not current_value:
                    item.setForeground(3, Qt.GlobalColor(Qt.darkYellow))
                    item.setText(3, "⚠️ Will create")
                else:
                    item.setForeground(3, Qt.GlobalColor(Qt.blue))
                    item.setText(3, "📝 Will update")
                
                self.results_tree.addTopLevelItem(item)
                self.preview_results.append({
                    'path': html_path,
                    'current': current_value,
                    'new': new_display
                })
                
            except Exception as e:
                item = QTreeWidgetItem([str(html_path.name), "Error", "", str(e)[:50]])
                item.setForeground(3, Qt.GlobalColor(Qt.red))
                self.results_tree.addTopLevelItem(item)
            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()
        
        self.progress.setVisible(False)
        self.results_tree.expandAll()
        self.apply_btn.setEnabled(True)
        self.summary_label.setText(f"Preview ready. Found {len(self.preview_results)} files to update.")

    def apply_changes(self):
        if not self.preview_results:
            QMessageBox.warning(self, "Warning", "No preview results. Click Preview first.")
            return
        
        reply = QMessageBox.question(self, "Confirm Batch Update",
                                     f"Update {len(self.preview_results)} files with new {self.meta_type.currentText()}?\n\n"
                                     f"This action cannot be undone easily. Consider running Backup first.\n\n"
                                     f"Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        tag_type = self.meta_type.currentText()
        new_value = self.new_value.toPlainText().strip()
        append_mode = self.append_mode.isChecked()
        separator = self.append_separator.text()
        
        self.apply_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.preview_results))
        
        updated = 0
        for idx, result in enumerate(self.preview_results):
            try:
                with open(result['path'], 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                self.update_value(soup, tag_type, new_value, append_mode, separator)
                
                with open(result['path'], 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                updated += 1
                
                # Update tree item status
                for i in range(self.results_tree.topLevelItemCount()):
                    item = self.results_tree.topLevelItem(i)
                    if item.text(0) == str(result['path'].relative_to(self.project_folder)):
                        item.setText(3, "✅ Updated")
                        item.setForeground(3, Qt.GlobalColor(Qt.darkGreen))
                        break
                
            except Exception as e:
                pass
            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()
        
        self.progress.setVisible(False)
        self.apply_btn.setEnabled(True)
        self.summary_label.setText(f"✅ Updated {updated} files with new {tag_type}.")
        QMessageBox.information(self, "Update Complete", f"Successfully updated {updated} files.")

    def update_theme(self, is_dark):
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    alternate-background-color: #3E4045;
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
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    alternate-background-color: #F8F9FA;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
