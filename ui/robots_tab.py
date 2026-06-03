import os
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup  # ← add this
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QGroupBox, QFormLayout,
    QLineEdit, QCheckBox, QTreeWidget, QTreeWidgetItem, QSplitter
)
from PySide6.QtCore import Qt


class RobotsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_root = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # project folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for HTML files")
        self.scan_btn.clicked.connect(self.scan_html_files)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # splitter: left (options), right (preview)
        splitter = QSplitter(Qt.Horizontal)

        # left: settings
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # robots.txt rules  # this is cursed but
        robots_group = QGroupBox("Robots.txt Rules")
        robots_layout = QVBoxLayout(robots_group)
        self.disallow_edit = QPlainTextEdit()
        self.disallow_edit.setPlaceholderText("Disallowed paths (one per line)\nExample:\n/admin/\n/private/")
        self.disallow_edit.setMaximumHeight(120)
        robots_layout.addWidget(QLabel("Disallow:"))
        robots_layout.addWidget(self.disallow_edit)
        self.allow_edit = QPlainTextEdit()
        self.allow_edit.setPlaceholderText("Allowed paths (one per line)\nExample:\n/public/\n/images/")
        self.allow_edit.setMaximumHeight(120)
        robots_layout.addWidget(QLabel("Allow:"))
        robots_layout.addWidget(self.allow_edit)
        self.sitemap_check = QCheckBox("Add sitemap URL to robots.txt")
        self.sitemap_check.setChecked(True)
        robots_layout.addWidget(self.sitemap_check)
        left_layout.addWidget(robots_group)

        # sitemap options
        sitemap_group = QGroupBox("Sitemap Options")
        sitemap_layout = QFormLayout(sitemap_group)
        self.priority_default = QLineEdit("0.5")
        sitemap_layout.addRow("Default priority (0.0-1.0):", self.priority_default)
        self.change_freq = QLineEdit("weekly")
        sitemap_layout.addRow("Change frequency:", self.change_freq)
        left_layout.addWidget(sitemap_group)

        # generate buttons row
        generate_row = QHBoxLayout()
        self.generate_btn = QPushButton("Generate robots.txt & sitemap.xml")
        self.generate_btn.clicked.connect(self.generate_files)
        self.image_sitemap_btn = QPushButton("Generate Image Sitemap")
        self.image_sitemap_btn.clicked.connect(self.generate_image_sitemap)
        self.video_sitemap_btn = QPushButton("Generate Video Sitemap")
        self.video_sitemap_btn.clicked.connect(self.generate_video_sitemap)
        generate_row.addWidget(self.generate_btn)
        generate_row.addWidget(self.image_sitemap_btn)
        generate_row.addWidget(self.video_sitemap_btn)
        left_layout.addLayout(generate_row)

        splitter.addWidget(left_widget)

        # right: preview & file list  # temporary solution
        right_widget = QWidget()

        right_layout = QVBoxLayout(right_widget)

        self.html_tree = QTreeWidget()
        self.html_tree.setHeaderLabels(["HTML Files Found"])
        right_layout.addWidget(QLabel("HTML files in project:"))
        right_layout.addWidget(self.html_tree)


        self.preview_robots = QPlainTextEdit()
        self.preview_robots.setReadOnly(True)
        self.preview_robots.setMaximumHeight(150)
        right_layout.addWidget(QLabel("Preview robots.txt:"))
        right_layout.addWidget(self.preview_robots)

        self.preview_sitemap = QPlainTextEdit()
        self.preview_sitemap.setReadOnly(True)
        self.preview_sitemap.setMaximumHeight(200)
        right_layout.addWidget(QLabel("Preview sitemap.xml:"))
        right_layout.addWidget(self.preview_sitemap)

        splitter.addWidget(right_widget)
        splitter.setSizes([350, 550])
        layout.addWidget(splitter)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.html_files = []

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Root Folder")
        if path:
            self.project_root = path
            self.folder_label.setText(path)
            self.status_label.setText(f"Project root: {path}")
            self.scan_html_files()

    def scan_html_files(self):
        if not self.project_root:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return
        self.html_files = list(Path(self.project_root).rglob("*.html"))
        self.html_tree.clear()
        for f in self.html_files:
            rel = f.relative_to(self.project_root)
            QTreeWidgetItem(self.html_tree, [str(rel)])
        self.status_label.setText(f"Found {len(self.html_files)} HTML files.")
        self.update_previews()

    def update_previews(self):
        robots_content = self.generate_robots_text()
        self.preview_robots.setPlainText(robots_content)
        sitemap_content = self.generate_sitemap_text()
        self.preview_sitemap.setPlainText(sitemap_content)

    def generate_robots_text(self):
        lines = ["User-agent: *"]
        allow_lines = [line.strip() for line in self.allow_edit.toPlainText().splitlines() if line.strip()]
        disallow_lines = [line.strip() for line in self.disallow_edit.toPlainText().splitlines() if line.strip()]

        if allow_lines:
            for a in allow_lines:
                lines.append(f"Allow: {a}")
        if disallow_lines:
            for d in disallow_lines:
                lines.append(f"Disallow: {d}")
        else:
            lines.append("Disallow:")

        if self.sitemap_check.isChecked() and self.project_root:
            sitemap_url = f"https://example.com/sitemap.xml"
            lines.append(f"Sitemap: {sitemap_url}")
        return "\n".join(lines)

    def generate_image_sitemap(self):
        if not self.html_files:
            QMessageBox.warning(self, "Warning", "Scan for HTML files first.")
            return
        
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
        lines.append('          xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">')
        

        for filepath in self.html_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                rel_path = filepath.relative_to(self.project_root)
                url = f"https://example.com/{rel_path.as_posix()}"
                lines.append(f"  <url>")

                lines.append(f"    <loc>{url}</loc>")
                
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src and not src.startswith('data:'):
                        lines.append(f"    <image:image>")
                        lines.append(f"      <image:loc>{src}</image:loc>")

                        if img.get('alt'):
                            lines.append(f"      <image:caption>{img['alt']}</image:caption>")
                        lines.append(f"    </image:image>")
                
                lines.append(f"  </url>")
            except:
                pass
        
        lines.append("</urlset>")
        
        output_path = Path(self.project_root) / "image-sitemap.xml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        QMessageBox.information(self, "Success", f"Image sitemap saved to:\n{output_path}")

    def generate_video_sitemap(self):
        if not self.html_files:
            QMessageBox.warning(self, "Warning", "Scan for HTML files first.")
            return
        
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
        lines.append('          xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">')
        
        for filepath in self.html_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                rel_path = filepath.relative_to(self.project_root)
                url = f"https://example.com/{rel_path.as_posix()}"
                

                if 'youtube.com/embed' in content or 'vimeo.com' in content:
                    lines.append(f"  <url>")
                    lines.append(f"    <loc>{url}</loc>")
                    lines.append(f"    <video:video>")
                    lines.append(f"      <video:thumbnail_loc>https://example.com/thumbnail.jpg</video:thumbnail_loc>")

                    lines.append(f"      <video:title>Video Title</video:title>")
                    lines.append(f"      <video:description>Video description</video:description>")
                    lines.append(f"      <video:player_loc>{url}</video:player_loc>")
                    lines.append(f"    </video:video>")
                    lines.append(f"  </url>")
            except:
                pass
        
        lines.append("</urlset>")
        
        output_path = Path(self.project_root) / "video-sitemap.xml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        QMessageBox.information(self, "Success", f"Video sitemap saved to:\n{output_path}")

    def generate_sitemap_text(self):
        if not self.html_files:
            return "<!-- No HTML files found -->"
        try:
            priority = float(self.priority_default.text())
        except:
            priority = 0.5

        changefreq = self.change_freq.text().strip() or "weekly"

        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for filepath in self.html_files:
            rel_path = filepath.relative_to(self.project_root)
            url = f"https://example.com/{rel_path.as_posix()}"
            lastmod = datetime.fromtimestamp(filepath.stat().st_mtime).date().isoformat()
            lines.append("  <url>")
            lines.append(f"    <loc>{url}</loc>")
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
            lines.append(f"    <changefreq>{changefreq}</changefreq>")
            lines.append(f"    <priority>{priority}</priority>")
            lines.append("  </url>")
        lines.append("</urlset>")
        return "\n".join(lines)


    def generate_files(self):
        if not self.project_root:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        robots_path = Path(self.project_root) / "robots.txt"
        robots_content = self.generate_robots_text()
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(robots_content)

        sitemap_path = Path(self.project_root) / "sitemap.xml"
        sitemap_content = self.generate_sitemap_text()
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)

        QMessageBox.information(self, "Success", f"Files created:\n{robots_path}\n{sitemap_path}")
        self.status_label.setText(f"Generated robots.txt and sitemap.xml in {self.project_root}")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.html_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    alternate-background-color: #3e4045;
                }
                QHeaderView::section {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
            """)
            self.preview_robots.setStyleSheet("background-color: #2b2d31; color: #e8e8e8;")
            self.preview_sitemap.setStyleSheet("background-color: #2b2d31; color: #e8e8e8;")
        else:
            self.html_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #ffffff;
                    color: #2c3e50;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #f1f3f5;
                    color: #2c3e50;
                    border: 1px solid #d0d7de;
                }
            """)
            self.preview_robots.setStyleSheet("background-color: #ffffff; color: #2c3e50;")
            self.preview_sitemap.setStyleSheet("background-color: #ffffff; color: #2c3e50;")
