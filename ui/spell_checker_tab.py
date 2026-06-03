"""

Aether Grammar & Spell Checker - Catch typos in HTML content
"""

import re
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


try:
    from spellchecker import SpellChecker
    HAS_SPELLCHECKER = True
except ImportError:
    HAS_SPELLCHECKER = False
    print("Install spellchecker: pip install pyspellchecker")


class SpellCheckerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.spell = None
        if HAS_SPELLCHECKER:
            self.spell = SpellChecker(language='en')
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # warning if spellchecker not installed
        if not HAS_SPELLCHECKER:
            warning = QLabel("\uf071 pyspellchecker not installed. Run: pip install pyspellchecker")
            warning.setStyleSheet("color: red; padding: 10px;")
            layout.addWidget(warning)

        # folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for Spelling Errors")
        self.scan_btn.clicked.connect(self.scan_spelling)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()

        layout.addLayout(folder_row)

        # options
        opts_layout = QHBoxLayout()
        self.check_english = QCheckBox("Check English")
        self.check_english.setChecked(True)
        self.ignore_numbers = QCheckBox("Ignore numbers")
        self.ignore_numbers.setChecked(True)
        self.ignore_caps = QCheckBox("Ignore ALL CAPS words")
        self.ignore_caps.setChecked(True)
        opts_layout.addWidget(self.check_english)
        opts_layout.addWidget(self.ignore_numbers)
        opts_layout.addWidget(self.ignore_caps)
        layout.addLayout(opts_layout)

        # results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Misspelled Word", "Context", "Suggestions"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.results_tree)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.summary_label = QLabel("Ready - Select a folder and click Scan")
        layout.addWidget(self.summary_label)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def is_valid_word(self, word):
        """Check if word should be checked"""
        if not word or len(word) < 2:
            return False

        if self.ignore_numbers.isChecked() and re.match(r'^[\d\.,]+$', word):
            return False
        if self.ignore_caps.isChecked() and word.isupper() and len(word) > 2:
            return False
        # skip common html/css/js keywords
        skip_words = {'div', 'span', 'class', 'id', 'href', 'src', 'alt', 'img', 'a', 'li', 'ul', 
                      'nav', 'footer', 'header', 'section', 'article', 'main', 'body', 'html', 
                      'head', 'meta', 'link', 'script', 'style', 'button', 'form', 'input'}
        if word.lower() in skip_words:
            return False
        return True

    def scan_spelling(self):
        if not HAS_SPELLCHECKER:
            QMessageBox.warning(self, "Warning", "Install pyspellchecker first:\npip install pyspellchecker")
            return
        
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.summary_label.setText("No HTML files found.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_tree.clear()
        
        error_count = 0

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))
                
                # extract text content (skip script/style tags)
                for tag in soup.find_all(['script', 'style']):
                    tag.decompose()
                
                text = soup.get_text()
                
                # split into words
                words = re.findall(r'\b[a-zA-Z\']+\b', text)
                
                # check each word
                misspelled = self.spell.unknown(words)
                
                for word in misspelled:
                    if not self.is_valid_word(word):
                        continue
                    
                    # get context (surrounding text)
                    context_match = re.search(r'[^\.!?]{0,50}' + re.escape(word) + r'[^\.!?]{0,50}', text, re.IGNORECASE)
                    context = context_match.group(0).strip() if context_match else word
                    
                    # get suggestions
                    suggestions = self.spell.candidates(word)
                    suggestions_text = ', '.join(list(suggestions)[:5]) if suggestions else "No suggestions"
                    

                    item = QTreeWidgetItem([rel_path, word, context[:80], suggestions_text])
                    self.results_tree.addTopLevelItem(item)
                    error_count += 1
                    
            except Exception as e:
                pass

            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        if error_count == 0:
            self.summary_label.setText(f"\uf00c No spelling errors found across {len(html_files)} files!")
        else:
            self.summary_label.setText(f"\uf071 Found {error_count} potential spelling errors across {len(html_files)} files")

    def update_theme(self, is_dark):
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    alternate-background-color: #3e4045;
                }
                QHeaderView::section {
                    background-color: #2b2d31;  # idk why this works but
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
            """)
        else:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #ffffff;
                    color: #2c3e50;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #f1f3f5;  # this is cursed but
                    color: #2c3e50;
                    border: 1px solid #d0d7de;
                }
            """)
