"""
Aether Keyword Density Analyzer - Track keyword usage to avoid stuffing or under-optimization
"""

import re
from collections import Counter
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QLineEdit,
    QGroupBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class KeywordDensityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.data_bridge = None
        self.current_results = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top controls
        top_row = QHBoxLayout()
        
        left_col = QVBoxLayout()
        
        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("\f07c Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        left_col.addLayout(folder_row)
        
        # Keyword input
        keyword_row = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keyword to analyze (e.g., 'web design')")
        self.keyword_input.setMinimumHeight(30)
        self.analyze_btn = QPushButton("\f002 Analyze Keyword Density")
        self.analyze_btn.clicked.connect(self.analyze_keyword)
        keyword_row.addWidget(self.keyword_input)
        keyword_row.addWidget(self.analyze_btn)
        left_col.addLayout(keyword_row)
        
        top_row.addLayout(left_col, 2)
        
        # Stats panel
        stats_group = QGroupBox("Keyword Statistics")
        stats_layout = QVBoxLayout(stats_group)
        self.stats_label = QLabel("Enter a keyword and click Analyze")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        top_row.addWidget(stats_group, 1)
        
        layout.addLayout(top_row)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["File", "Keyword", "Count", "Density %", "Status"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)

        # Density guidelines
        guidelines = QLabel(
            "\f201 Keyword Density Guidelines:\n"
            "• < 0.5%: \f071 Under-optimized - add more keyword variations\n"
            "• 0.5% - 3.0%: \f00c Optimal range\n"
            "• > 3.0%: \58 Keyword stuffing - reduce usage to avoid penalties"
        )
        guidelines.setWordWrap(True)
        guidelines.setStyleSheet("padding: 8px; border-radius: 4px; margin-top: 5px;")
        layout.addWidget(guidelines)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.summary_label = QLabel("Ready - Select a folder, enter a keyword, and click Analyze")
        layout.addWidget(self.summary_label)

        self.current_results = []

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def clean_text(self, text):
        """Remove punctuation and normalize text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_keyword_variations(self, keyword):
        """Generate variations of the keyword (singular/plural, common forms)"""
        variations = {keyword}
        
        # Add singular/plural variations
        if keyword.endswith('s'):
            variations.add(keyword[:-1])
        else:
            variations.add(keyword + 's')
        
        # Add common suffixes
        for suffix in ['ing', 'ed', 'er', 'or']:
            variations.add(keyword + suffix)
        
        return variations

    def analyze_keyword(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a folder first.")
            return
        
        keyword = self.keyword_input.text().strip().lower()
        if not keyword:
            QMessageBox.warning(self, "Warning", "Enter a keyword to analyze.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.summary_label.setText("No HTML files found.")
            return

        self.analyze_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_table.setRowCount(0)
        self.current_results = []

        total_words = 0
        total_keyword_count = 0
        keyword_variations = self.get_keyword_variations(keyword)
        issue_count = 0

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                # Remove script and style tags
                for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    tag.decompose()
                
                # Get main content text
                text = soup.get_text()
                cleaned_text = self.clean_text(text)
                words = cleaned_text.split()
                
                word_count = len(words)
                if word_count == 0:
                    continue
                
                # Count keyword occurrences (including variations)
                keyword_count = 0
                for variation in keyword_variations:
                    keyword_count += cleaned_text.count(variation)
                
                density = (keyword_count / word_count) * 100 if word_count > 0 else 0
                
                # Determine status
                if density < 0.5:
                    status = "\f071 Under-optimized"
                    status_color = "orange"
                    issue_count += 1
                elif density > 3.0:
                    status = "\58 Keyword Stuffing!"
                    status_color = "red"
                    issue_count += 1
                else:
                    status = "\f00c Good"
                    status_color = "green"
                
                rel_path = str(html_path.relative_to(self.project_folder))
                
                row = self.results_table.rowCount()
                self.results_table.insertRow(row)
                self.results_table.setItem(row, 0, QTableWidgetItem(rel_path))
                self.results_table.setItem(row, 1, QTableWidgetItem(keyword))
                self.results_table.setItem(row, 2, QTableWidgetItem(str(keyword_count)))
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{density:.2f}%"))
                
                status_item = QTableWidgetItem(status)
                if status_color == "green":
                    status_item.setForeground(Qt.GlobalColor(Qt.darkGreen))
                elif status_color == "orange":
                    status_item.setForeground(Qt.GlobalColor(Qt.darkYellow))
                else:
                    status_item.setForeground(Qt.GlobalColor(Qt.red))
                self.results_table.setItem(row, 4, status_item)
                
                total_words += word_count
                total_keyword_count += keyword_count
                
                self.current_results.append({
                    'file': rel_path,
                    'keyword_count': keyword_count,
                    'word_count': word_count,
                    'density': density,
                    'status': status
                })
                
            except Exception as e:
                pass
            
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.analyze_btn.setEnabled(True)
        
        # Report to dashboard
        if self.data_bridge:
            self.data_bridge.report_scan(len(html_files), issue_count, 0)
        
        # Update stats
        overall_density = (total_keyword_count / total_words) * 100 if total_words > 0 else 0
        
        if overall_density < 0.5:
            recommendation = "\f071 Overall keyword density is LOW. Consider adding more keyword variations naturally."
            rec_color = "orange"
        elif overall_density > 3.0:
            recommendation = "\58 Overall keyword density is HIGH. Reduce keyword usage to avoid penalties."
            rec_color = "red"
        else:
            recommendation = "\f00c Overall keyword density is GOOD (0.5-3.0%). Keep up the natural writing!"
            rec_color = "green"
        
        stats_text = f"""
\f201 Overall Statistics:
• Total words analyzed: {total_words:,}
• Total keyword mentions: {total_keyword_count}
• Overall density: {overall_density:.2f}%

\f140 Recommendation:
<span style='color:{rec_color}'>{recommendation}</span>

\f0eb Ideal keyword density: 0.5% - 3.0%
• Below 0.5%: Too low, may not rank
• Above 3.0%: Risk of keyword stuffing penalty
"""
        self.stats_label.setText(stats_text)
        self.summary_label.setText(f"\f00c Analyzed {len(html_files)} files for keyword '{keyword}'")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.results_table.setStyleSheet("""
                QTableWidget {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    alternate-background-color: #3E4045;
                    gridline-color: #3E4045;
                }
                QHeaderView::section {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
            """)
        else:
            self.results_table.setStyleSheet("""
                QTableWidget {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    alternate-background-color: #F8F9FA;
                    gridline-color: #D0D7DE;
                }
                QHeaderView::section {
                    background-color: #F1F3F5;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
            """)
