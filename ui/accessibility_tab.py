import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QTabWidget, QApplication, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class AccessibilityTab(QWidget):
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
        self.scan_btn = QPushButton("Scan for Accessibility Issues")
        self.scan_btn.clicked.connect(self.scan_accessibility)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Options
        opts_group = QGroupBox("Scan Options")
        opts_layout = QHBoxLayout()
        self.check_alt = QCheckBox("Missing alt text")
        self.check_alt.setChecked(True)
        self.check_lang = QCheckBox("Missing html lang")
        self.check_lang.setChecked(True)
        self.check_empty_links = QCheckBox("Empty links (without text or aria-label)")
        self.check_empty_links.setChecked(True)
        self.check_headings = QCheckBox("Heading hierarchy")
        self.check_headings.setChecked(True)
        self.check_iframes = QCheckBox("Missing iframe titles")
        self.check_iframes.setChecked(True)
        self.check_labels = QCheckBox("Missing form labels")
        self.check_labels.setChecked(True)
        opts_layout.addWidget(self.check_alt)
        opts_layout.addWidget(self.check_lang)
        opts_layout.addWidget(self.check_empty_links)
        opts_layout.addWidget(self.check_headings)
        opts_layout.addWidget(self.check_iframes)
        opts_layout.addWidget(self.check_labels)
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Issue Type", "File", "Element", "Description"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.results_tree)

        # Summary
        self.summary_label = QLabel("Ready - Select a folder and click Scan")
        layout.addWidget(self.summary_label)

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.fix_btn = QPushButton("Fix Selected Issues (Coming Soon)")
        self.fix_btn.setEnabled(False)
        layout.addWidget(self.fix_btn)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def log_msg(self, msg):
        self.summary_label.setText(msg)
        QApplication.processEvents()

    def scan_accessibility(self):
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
        self.results = []

        issue_counts = {
            "missing_alt": 0,
            "missing_lang": 0,
            "empty_links": 0,
            "heading_issues": 0,
            "missing_iframe_title": 0,
            "missing_labels": 0
        }

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))

                # 1. Missing alt text on images
                if self.check_alt.isChecked():
                    for img in soup.find_all('img'):
                        alt = img.get('alt', '')
                        if not alt or alt.strip() == '':
                            self._add_result("Missing alt text", rel_path, f"<img src='{img.get('src', '?')[:50]}'>", "Add descriptive alt attribute")
                            issue_counts["missing_alt"] += 1

                # 2. Missing html lang attribute
                if self.check_lang.isChecked():
                    html_tag = soup.find('html')
                    if html_tag and not html_tag.get('lang'):
                        self._add_result("Missing html lang", rel_path, "<html>", "Add lang attribute (e.g., lang='en', lang='fa')")
                        issue_counts["missing_lang"] += 1

                # 3. Empty links (with no accessible text) – IMPROVED
                if self.check_empty_links.isChecked():
                    for a in soup.find_all('a', href=True):
                        visible_text = a.get_text(strip=True)
                        img_inside = a.find('img')
                        img_has_alt = img_inside and img_inside.get('alt', '').strip()
                        aria_label = a.get('aria-label', '').strip()
                        
                        if visible_text or img_has_alt or aria_label:
                            continue
                        
                        href = a.get('href', '').strip()
                        
                        # Skip common skip-links and empty anchors
                        if href in ['#', '#main', '#content', '#main-content', 'javascript:void(0)', '']:
                            continue
                        
                        # For navigation links (../, ./) or file paths, lower priority but still flag
                        if href.startswith('../') or href.startswith('./') or '.' in href or '/' in href:
                            self._add_result("Empty link (navigation)", rel_path, f"<a href='{href}'>", f"Add text or aria-label. URL: {href}")
                        else:
                            self._add_result("Empty link", rel_path, f"<a href='{href}'>", "Add text content or aria-label")
                        issue_counts["empty_links"] += 1

                # 4. Heading hierarchy and SEO checks
                if self.check_headings.isChecked():
                    h1_tags = soup.find_all('h1')
                    h1_count = len(h1_tags)
                    
                    if h1_count == 0:
                        self._add_result("Missing h1", rel_path, "No h1 tag found", 
                                        "Add exactly ONE h1 tag for the main page title (critical for SEO and accessibility)")
                        issue_counts["heading_issues"] += 1
                    elif h1_count > 1:
                        self._add_result("Multiple h1 tags", rel_path, f"{h1_count} h1 tags found", 
                                        "Use only ONE h1 per page. Convert extra h1 tags to h2-h6 (bad for SEO)")
                        issue_counts["heading_issues"] += 1
                    
                    # Check heading hierarchy (no skipping levels)
                    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    expected_level = 1
                    
                    for heading in headings:
                        current_level = int(heading.name[1])
                        text_preview = heading.get_text(strip=True)[:50]
                        
                        # Only check if we already passed through h1 validation
                        if current_level > expected_level + 1:
                            self._add_result("Heading level skip", rel_path, 
                                        f"<{heading.name}> {text_preview}", 
                                        f"Don't skip from h{expected_level} to h{current_level}. Use h{expected_level+1} instead")
                            issue_counts["heading_issues"] += 1
                            # Continue without updating expected level to avoid false positives
                        else:
                            expected_level = current_level

                # 5. Missing iframe title
                if self.check_iframes.isChecked():
                    for iframe in soup.find_all('iframe'):
                        if not iframe.get('title'):
                            self._add_result("Missing iframe title", rel_path, f"<iframe src='{iframe.get('src', '?')[:50]}'>", "Add title attribute for screen readers")
                            issue_counts["missing_iframe_title"] += 1

                # 6. Missing form labels
                if self.check_labels.isChecked():
                    for input_tag in soup.find_all(['input', 'textarea', 'select']):
                        if input_tag.get('type') in ['hidden', 'submit', 'button', 'reset']:
                            continue
                        input_id = input_tag.get('id')
                        if input_id:
                            label = soup.find('label', attrs={'for': input_id})
                            if not label and not input_tag.get('aria-label'):
                                self._add_result("Missing label", rel_path, f"<{input_tag.name} id='{input_id}'>", "Add <label for='{input_id}'> or aria-label")
                                issue_counts["missing_labels"] += 1
                        elif not input_tag.get('aria-label'):
                            self._add_result("Missing label", rel_path, f"<{input_tag.name}>", "Add id + label, or aria-label")
                            issue_counts["missing_labels"] += 1

            except Exception as e:
                self._add_result("Parse error", rel_path, "", str(e)[:100])

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)

        total = sum(issue_counts.values())
        summary_text = f"✅ Scan complete! Found {total} accessibility issues across {len(html_files)} files.\n"
        summary_text += f"  • Missing alt: {issue_counts['missing_alt']}\n"
        summary_text += f"  • Missing lang: {issue_counts['missing_lang']}\n"
        summary_text += f"  • Empty links: {issue_counts['empty_links']}\n"
        summary_text += f"  • Heading issues: {issue_counts['heading_issues']}\n"
        summary_text += f"  • Iframe no title: {issue_counts['missing_iframe_title']}\n"
        summary_text += f"  • Missing labels: {issue_counts['missing_labels']}"
        self.log_msg(summary_text)

        QMessageBox.information(self, "Scan Complete", f"Found {total} accessibility issues.\nCheck the results panel for details.")

    def _add_result(self, issue_type, file_path, element, description):
        item = QTreeWidgetItem([issue_type, file_path, element, description])
        self.results_tree.addTopLevelItem(item)
        self.results.append({
            "type": issue_type,
            "file": file_path,
            "element": element,
            "description": description
        })

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
