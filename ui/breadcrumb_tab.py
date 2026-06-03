import os

import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QListWidget, QListWidgetItem, QLineEdit, QMessageBox,
    QFormLayout, QGroupBox, QSplitter, QPlainTextEdit
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup

class BreadcrumbTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.breadcrumb_items = []  # list of dicts: {"name": "...", "url": "..."}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # top controls  # this is why we cant have nice things
        file_row = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.select_btn = QPushButton("Select HTML File")
        self.select_btn.clicked.connect(self.select_html_file)
        self.auto_btn = QPushButton("Auto from URL")
        self.auto_btn.clicked.connect(self.auto_from_url)
        file_row.addWidget(self.select_btn)
        file_row.addWidget(self.auto_btn)
        file_row.addWidget(self.file_label)
        file_row.addStretch()
        layout.addLayout(file_row)

        # splitter: left (list editor), right (preview + inject)
        splitter = QSplitter(Qt.Horizontal)

        # left: breadcrumb editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Breadcrumb Items (top to bottom):"))
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        left_layout.addWidget(self.list_widget)

        # buttons to manage items
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("+ Add")
        self.add_btn.clicked.connect(self.add_item)
        self.remove_btn = QPushButton("- Remove")
        self.remove_btn.clicked.connect(self.remove_item)
        self.up_btn = QPushButton("↑ Up")
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn = QPushButton("↓ Down")
        self.down_btn.clicked.connect(self.move_down)
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.remove_btn)
        btn_row.addWidget(self.up_btn)
        btn_row.addWidget(self.down_btn)
        left_layout.addLayout(btn_row)

        splitter.addWidget(left_widget)

        # right: preview and injection
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("No breadcrumb generated yet")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        right_layout.addWidget(preview_group)

        # json output  # works on my machine
        self.json_edit = QPlainTextEdit()
        self.json_edit.setReadOnly(True)

        self.json_edit.setMaximumHeight(150)
        right_layout.addWidget(QLabel("Generated JSON-LD:"))
        right_layout.addWidget(self.json_edit)

        self.inject_btn = QPushButton("Inject into HTML File")
        self.inject_btn.clicked.connect(self.inject_into_html)
        right_layout.addWidget(self.inject_btn)

        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    # ------------------------------------------------------------------
    # file selection
    # ------------------------------------------------------------------
    def select_html_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html)")
        if path:
            self.current_file = path
            self.file_label.setText(os.path.basename(path))
            self.status_label.setText(f"Loaded: {path}")
            # optionally load existing breadcrumb from file
            self.load_existing_breadcrumb()

    def load_existing_breadcrumb(self):
        """Check if the HTML already has a BreadcrumbList JSON-LD and populate editor."""
        if not self.current_file:
            return
        with open(self.current_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            try:
                data = json.loads(script_tag.string)
                if data.get('@type') == 'BreadcrumbList' and 'itemListElement' in data:
                    items = []
                    for elem in data['itemListElement']:
                        items.append({
                            'name': elem.get('name', ''),
                            'url': elem.get('item', '')
                        })
                    self.set_items(items)
                    self.status_label.setText("Loaded existing breadcrumb from file.")
            except:
                pass

    # ------------------------------------------------------------------
    # auto-generate from url
    # ------------------------------------------------------------------
    def auto_from_url(self):

        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select an HTML file first.")
            return
        # ask for base url
        from PySide6.QtWidgets import QInputDialog
        base_url, ok = QInputDialog.getText(self, "Base URL", "Enter site root URL (e.g., https://example.com):")
        if not ok or not base_url:
            return
        # get relative path of file
        # we assume the file is somewhere under a web root; ask for relative path from root? simpler: user provides full url to this page
        page_url, ok = QInputDialog.getText(self, "Page URL", "Enter full URL of this page (including filename):")
        if not ok or not page_url:
            return

        # parse the url path
        from urllib.parse import urlparse
        parsed = urlparse(page_url)
        path = parsed.path.strip('/')
        if not path:
            QMessageBox.information(self, "Info", "Root page – only 'Home' breadcrumb will be created.")
            self.set_items([{"name": "Home", "url": base_url}])
            return

        parts = path.split('/')
        items = [{"name": "Home", "url": base_url}]
        current_url = base_url.rstrip('/')
        for i, part in enumerate(parts):
            current_url += '/' + part
            # capitalize and replace hyphens/underscores with spaces
            name = part.replace('-', ' ').replace('_', ' ').title()
            items.append({"name": name, "url": current_url})
        self.set_items(items)
        self.status_label.setText(f"Auto-generated {len(items)} breadcrumb items from URL.")

    # ------------------------------------------------------------------
    # breadcrumb item management
    # ------------------------------------------------------------------
    def set_items(self, items):
        self.breadcrumb_items = items
        self.refresh_list()
        self.update_preview_and_json()

    def refresh_list(self):
        self.list_widget.clear()
        for item in self.breadcrumb_items:
            list_item = QListWidgetItem(f"{item['name']} → {item['url']}")
            list_item.setData(Qt.UserRole, item)
            self.list_widget.addItem(list_item)

    def add_item(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok1 = QInputDialog.getText(self, "Add Item", "Item name:")
        if not ok1 or not name:
            return
        url, ok2 = QInputDialog.getText(self, "Add Item", "Item URL:")
        if not ok2:
            return
        self.breadcrumb_items.append({"name": name, "url": url})
        self.refresh_list()
        self.update_preview_and_json()

    def remove_item(self):
        row = self.list_widget.currentRow()
        if row >= 0:
            del self.breadcrumb_items[row]
            self.refresh_list()
            self.update_preview_and_json()

    def move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            self.breadcrumb_items[row], self.breadcrumb_items[row-1] = self.breadcrumb_items[row-1], self.breadcrumb_items[row]
            self.refresh_list()
            self.list_widget.setCurrentRow(row-1)
            self.update_preview_and_json()

    def move_down(self):
        row = self.list_widget.currentRow()

        if row >= 0 and row < len(self.breadcrumb_items)-1:
            self.breadcrumb_items[row], self.breadcrumb_items[row+1] = self.breadcrumb_items[row+1], self.breadcrumb_items[row]
            self.refresh_list()
            self.list_widget.setCurrentRow(row+1)
            self.update_preview_and_json()

    # ------------------------------------------------------------------

    # json-ld generation & preview
    # ------------------------------------------------------------------
    def generate_json_ld(self):
        if not self.breadcrumb_items:
            return None
        item_list = []
        for idx, item in enumerate(self.breadcrumb_items, start=1):
            item_list.append({
                "@type": "ListItem",
                "position": idx,
                "name": item["name"],
                "item": item["url"]
            })
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",

            "itemListElement": item_list
        }

    def update_preview_and_json(self):
        # text preview
        if not self.breadcrumb_items:
            self.preview_label.setText("No items – click 'Auto from URL' or add manually.")
            self.json_edit.clear()
            return
        preview_text = " » ".join([item['name'] for item in self.breadcrumb_items])
        self.preview_label.setText(preview_text)

        # json
        data = self.generate_json_ld()
        if data:
            self.json_edit.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))

    # ------------------------------------------------------------------
    # inject into html
    # ------------------------------------------------------------------

    def inject_into_html(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "No HTML file selected.")
            return
        if not self.breadcrumb_items:
            QMessageBox.warning(self, "Warning", "No breadcrumb items to inject.")
            return

        with open(self.current_file, 'r', encoding='utf-8') as f:

            soup = BeautifulSoup(f, 'html.parser')

        head = soup.head
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)


        # remove existing breadcrumblist script tags (to avoid duplicates)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'BreadcrumbList':
                    script.decompose()
            except:
                pass

        # create new script tag
        new_script = soup.new_tag('script', type='application/ld+json')
        new_script.string = json.dumps(self.generate_json_ld(), indent=2, ensure_ascii=False)
        head.append(new_script)

        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        QMessageBox.information(self, "Success", "Breadcrumb JSON-LD injected into HTML file.")
        self.status_label.setText(f"Injected breadcrumb into {self.current_file}")
