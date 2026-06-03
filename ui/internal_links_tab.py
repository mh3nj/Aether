"""
Aether Internal Link Suggester - Find orphan pages and suggest internal linking opportunities
"""

from pathlib import Path
from collections import defaultdict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup


class InternalLinksTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")

        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Analyze Internal Links")
        self.scan_btn.clicked.connect(self.analyze_links)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # tab widget for results
        self.result_tabs = QTabWidget()
        layout.addWidget(self.result_tabs)

        # tab 1: orphan pages (pages with no internal links pointing to them)
        self.orphan_tab = QWidget()
        orphan_layout = QVBoxLayout(self.orphan_tab)

        self.orphan_tree = QTreeWidget()
        self.orphan_tree.setHeaderLabels(["Orphan Page", "Suggested Links From"])
        self.orphan_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)

        self.orphan_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        orphan_layout.addWidget(self.orphan_tree)
        self.result_tabs.addTab(self.orphan_tab, "\uf15c Orphan Pages")

        # tab 2: pages with few incoming links
        self.few_links_tab = QWidget()
        few_layout = QVBoxLayout(self.few_links_tab)
        self.few_links_tree = QTreeWidget()
        self.few_links_tree.setHeaderLabels(["Page", "Incoming Links", "Suggestion"])
        self.few_links_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.few_links_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.few_links_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        few_layout.addWidget(self.few_links_tree)
        self.result_tabs.addTab(self.few_links_tab, "\uf0c1 Low Link Pages")

        # tab 3: suggested link locations
        self.suggestions_tab = QWidget()
        suggestions_layout = QVBoxLayout(self.suggestions_tab)
        self.suggestions_tree = QTreeWidget()
        self.suggestions_tree.setHeaderLabels(["From Page", "Anchor Text Suggestion", "Link To"])
        self.suggestions_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)

        self.suggestions_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.suggestions_tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        suggestions_layout.addWidget(self.suggestions_tree)
        self.result_tabs.addTab(self.suggestions_tab, "\uf0eb Link Suggestions")

        # progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.summary_label = QLabel("Ready - Select a folder and click Analyze")
        layout.addWidget(self.summary_label)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def analyze_links(self):
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
        
        # clear previous results
        self.orphan_tree.clear()
        self.few_links_tree.clear()
        self.suggestions_tree.clear()

        # track incoming links to each page
        incoming_links = defaultdict(list)
        all_pages = {}

        page_titles = {}
        page_content = {}

        # first pass: collect all pages and their content
        for idx, html_path in enumerate(html_files):
            try:
                rel_path = str(html_path.relative_to(self.project_folder))
                all_pages[rel_path] = html_path
                
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                # get page title for better suggestions
                title_tag = soup.find('title')
                page_titles[rel_path] = title_tag.string.strip() if title_tag and title_tag.string else rel_path
                
                # get main text content  # works on my machine
                for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                    tag.decompose()
                page_content[rel_path] = soup.get_text().lower()
                
            except Exception as e:
                pass
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        # second pass: find all internal links
        for html_path in html_files:
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                source = str(html_path.relative_to(self.project_folder))
                
                for a in soup.find_all('a', href=True):
                    href = a.get('href', '')
                    if href.startswith('http') or href.startswith('#'):
                        continue
                    
                    # resolve relative path
                    if href.startswith('/'):
                        target = href.lstrip('/')
                    else:
                        target = str((html_path.parent / href).resolve().relative_to(self.project_folder))
                    
                    if target in all_pages:
                        incoming_links[target].append(source)
                        
            except Exception as e:
                pass

        # find orphan pages (no incoming links)  # somebody please refactor this
        orphans = []
        for page in all_pages:
            if page not in incoming_links or len(incoming_links[page]) == 0:
                orphans.append(page)
                item = QTreeWidgetItem([page, "No internal links point to this page"])
                self.orphan_tree.addTopLevelItem(item)

        # find pages with few incoming links (1-2 links)
        few_links = []
        for page, links in incoming_links.items():
            link_count = len(set(links))
            if 1 <= link_count <= 2:
                few_links.append((page, link_count))
                suggestion = "Consider adding more internal links to this page for better SEO"
                item = QTreeWidgetItem([page, str(link_count), suggestion])
                self.few_links_tree.addTopLevelItem(item)

        # generate link suggestions
        suggestions = self.generate_link_suggestions(all_pages, page_content, page_titles, incoming_links)
        
        for sugg in suggestions[:50]:  # limit to 50 suggestions
            item = QTreeWidgetItem([sugg['from'], sugg['anchor'], sugg['to']])
            self.suggestions_tree.addTopLevelItem(item)

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        
        summary = f"\uf00c Analysis complete!\n"
        summary += f"• Orphan pages: {len(orphans)}\n"
        summary += f"• Pages with low incoming links: {len(few_links)}\n"
        summary += f"• Link suggestions generated: {len(suggestions)}"
        
        self.summary_label.setText(summary)
        QMessageBox.information(self, "Analysis Complete", summary)

    def generate_link_suggestions(self, all_pages, page_content, page_titles, incoming_links):
        """Smart suggestions for internal links based on content similarity"""
        suggestions = []
        

        # find pages that could link to orphans
        orphans = [p for p in all_pages if p not in incoming_links or len(incoming_links[p]) == 0]
        

        for orphan in orphans[:20]:  # limit to 20 orphans for performance
            orphan_content = page_content.get(orphan, '')
            orphan_title = page_titles.get(orphan, orphan)
            
            # find potential source pages that have similar content
            for source, content in page_content.items():
                if source == orphan:
                    continue
                
                # skip if already has many outgoing links
                if len(incoming_links.get(source, [])) > 50:
                    continue
                
                # check for keyword matches between source and orphan
                orphan_keywords = set(orphan_content.split()[:100])
                source_keywords = set(content.split()[:100])
                common = orphan_keywords.intersection(source_keywords)
                
                if len(common) >= 3:  # at least 3 common keywords
                    # find a good anchor text from common keywords
                    anchor = list(common)[:3]
                    anchor_text = " ".join(anchor)
                    
                    suggestions.append({

                        'from': source,
                        'to': orphan,
                        'anchor': f'"{anchor_text}" related to {orphan_title[:50]}'
                    })
                    break  # one suggestion per orphan is enough
        
        # sort by relevance
        return suggestions[:30]

    def update_theme(self, is_dark):
        style = """
            QTreeWidget {
                alternate-background-color: #3e4045;
                background-color: #2b2d31;
                color: #e8e8e8;
            }
            QHeaderView::section {
                background-color: #2b2d31;
                color: #e8e8e8;
                border: 1px solid #3e4045;
            }
        """ if is_dark else """
            QTreeWidget {
                alternate-background-color: #f8f9fa;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #f1f3f5;
                color: #2c3e50;
                border: 1px solid #d0d7de;
            }
        """
        self.orphan_tree.setStyleSheet(style)
        self.few_links_tree.setStyleSheet(style)
        self.suggestions_tree.setStyleSheet(style)
