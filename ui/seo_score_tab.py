"""
Aether SEO Score Tab – 0-100 scoring per page with recommendations
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup
from ui.data_bridge import DataBridge


class SEOScoreTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.data_bridge = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Analyze SEO Scores")
        self.scan_btn.clicked.connect(self.analyze)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Page", "Score", "Title", "Description", "Issues"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.results_tree)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Tips section
        tips_group = QGroupBox("📖 SEO Best Practices & Score Guide")
        tips_layout = QVBoxLayout(tips_group)
        tips_text = QLabel(
            "📝 **Title Tag:** 50-60 characters – Include primary keyword near beginning\n\n"
            "📄 **Meta Description:** 150-160 characters – Natural keywords + call-to-action\n\n"
            "🏷️ **H1 Heading:** Exactly ONE per page – Describes the main topic\n\n"
            "🖼️ **Image Alt Text:** Describes image for screen readers and SEO\n\n"
            "📱 **Viewport:** Required for mobile-friendly ranking (Google mobile-first index)\n\n"
            "⭐ **Score Guide:**\n"
            "   • 80-100: \f00c Excellent – Optimized for search engines\n"
            "   • 60-79:  \f071 Needs Improvement – Fix critical issues\n"
            "   • 0-59:   \58 Critical – Major SEO problems detected"
        )
        tips_text.setWordWrap(True)
        tips_layout.addWidget(tips_text)
        layout.addWidget(tips_group)

        self.summary_label = QLabel("Ready - Select a folder and click Analyze")
        layout.addWidget(self.summary_label)

        self.total_pages = 0
        self.total_issues = 0

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def set_data_bridge(self, bridge):
        """Set the data bridge for dashboard communication"""
        self.data_bridge = bridge

    def analyze(self):
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

        scores = []
        issues_per_page = []

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                score = 100
                issues = []
                title = ""
                description = ""

                # Title check (-30 max)
                title_tag = soup.find('title')
                if not title_tag or not title_tag.string:
                    score -= 30
                    issues.append("\58 Missing title tag")
                    title = "(missing)"
                else:
                    title = title_tag.string.strip()
                    length = len(title)
                    if length < 30:
                        score -= 15
                        issues.append(f"Title too short ({length} chars - need 50-60)")
                    elif length < 50:
                        score -= 10
                        issues.append(f"Title slightly short ({length} chars - aim for 50-60)")
                    elif length > 60:
                        score -= 10
                        issues.append(f"Title too long ({length} chars - Google truncates after 60)")

                # Meta description check (-30 max)
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if not meta_desc or not meta_desc.get('content'):
                    score -= 30
                    issues.append("\58 Missing meta description")
                    description = "(missing)"
                else:
                    description = meta_desc['content']
                    length = len(description)
                    if length < 120:
                        score -= 10
                        issues.append(f"Description too short ({length} chars - need 150-160)")
                    elif length > 160:
                        score -= 10
                        issues.append(f"Description too long ({length} chars - truncates on mobile)")

                # H1 check (-20 max)
                h1_tags = soup.find_all('h1')
                h1_count = len(h1_tags)
                if h1_count == 0:
                    score -= 20
                    issues.append("\58 No H1 tag - critical for structure")
                elif h1_count > 1:
                    score -= 10
                    issues.append(f"\f071 {h1_count} H1 tags - use only one")

                # Image alt text (-15 max)
                img_tags = soup.find_all('img')
                missing_alt = sum(1 for img in img_tags if not img.get('alt'))
                if missing_alt > 0:
                    penalty = min(15, missing_alt * 2)
                    score -= penalty
                    issues.append(f"{missing_alt} images missing alt text (-{penalty})")

                # Viewport check (-5)
                if not soup.find('meta', attrs={'name': 'viewport'}):
                    score -= 5
                    issues.append("Missing viewport meta tag (not mobile-friendly)")

                score = max(0, min(100, score))
                scores.append(score)
                issues_per_page.append(len(issues))
                
                # Color code based on score
                if score >= 80:
                    color = Qt.green
                elif score >= 60:
                    color = Qt.yellow
                else:
                    color = Qt.red

                item = QTreeWidgetItem([
                    html_path.name,
                    f"{score}%",
                    title[:60],
                    description[:80],
                    ", ".join(issues[:3]) + ("..." if len(issues) > 3 else "")
                ])
                for col in range(5):
                    item.setForeground(col, color)
                self.results_tree.addTopLevelItem(item)

            except Exception as e:
                item = QTreeWidgetItem([html_path.name, "0%", "Error", "", str(e)[:50]])
                for col in range(5):
                    item.setForeground(col, Qt.red)
                self.results_tree.addTopLevelItem(item)
                scores.append(0)
                issues_per_page.append(1)

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        # Calculate averages
        total_scores = sum(scores)
        avg_score = int(total_scores / len(scores)) if scores else 0
        total_issues = sum(issues_per_page)
        
        # Send data to dashboard via bridge
        if self.data_bridge:
            self.data_bridge.report_scan(len(html_files), total_issues, avg_score)
        
        self.summary_label.setText(f"\f00c Analyzed {len(html_files)} pages | Avg Score: {avg_score}% | Total Issues: {total_issues}")
        
        QMessageBox.information(self, "Analysis Complete", 
            f"📊 SEO Score Analysis\n\n"
            f"Pages scanned: {len(html_files)}\n"
            f"Average score: {avg_score}%\n"
            f"Total issues found: {total_issues}\n\n"
            f"Check the results table for details on each page.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
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
