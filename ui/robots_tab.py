import os
from pathlib import Path
from datetime import datetime
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

        # Project folder selection
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

        # Splitter: left (options), right (preview)
        splitter = QSplitter(Qt.Horizontal)

        # Left: settings
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Robots.txt rules
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

        # Sitemap options
        sitemap_group = QGroupBox("Sitemap Options")
        sitemap_layout = QFormLayout(sitemap_group)
        self.priority_default = QLineEdit("0.5")
        sitemap_layout.addRow("Default priority (0.0-1.0):", self.priority_default)
        self.change_freq = QLineEdit("weekly")
        sitemap_layout.addRow("Change frequency:", self.change_freq)
        left_layout.addWidget(sitemap_group)

        # Generate button
        self.generate_btn = QPushButton("Generate robots.txt & sitemap.xml")
        self.generate_btn.clicked.connect(self.generate_files)
        left_layout.addWidget(self.generate_btn)

        splitter.addWidget(left_widget)

        # Right: preview & file list
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
        # Update robots.txt preview
        robots_content = self.generate_robots_text()
        self.preview_robots.setPlainText(robots_content)

        # Update sitemap preview
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
            # Assume sitemap will be placed at root
            sitemap_url = f"https://example.com/sitemap.xml"  # user should replace domain
            lines.append(f"Sitemap: {sitemap_url}")
        return "\n".join(lines)

    def generate_image_sitemap(self):
        """Generate sitemap with images for Google Images SEO"""
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
                
                rel_path = filepath.relative_to(self.project_folder)
                url = f"https://example.com/{rel_path.as_posix()}"
                lines.append(f"  <url>")
                lines.append(f"    <loc>{url}</loc>")
                
                # Find all images
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
        
        output_path = Path(self.project_folder) / "image-sitemap.xml"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        QMessageBox.information(self, "Success", f"Image sitemap saved to:\n{output_path}")

    def generate_video_sitemap(self):
        """Generate video sitemap for Google Video SEO"""
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
                
                # Look for video embeds
                rel_path = filepath.relative_to(self.project_folder)
                url = f"https://example.com/{rel_path.as_posix()}"
                
                # Simple video detection (YouTube, Vimeo, etc.)
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
        
        output_path = Path(self.project_folder) / "video-sitemap.xml"
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
            # Convert to URL (placeholder – user will replace domain)
            url = f"https://example.com/{rel_path.as_posix()}"
            # Get last modified if possible
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

        # Write robots.txt
        robots_path = Path(self.project_root) / "robots.txt"
        robots_content = self.generate_robots_text()
        with open(robots_path, "w", encoding="utf-8") as f:
            f.write(robots_content)

        # Write sitemap.xml
        sitemap_path = Path(self.project_root) / "sitemap.xml"
        sitemap_content = self.generate_sitemap_text()
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(sitemap_content)

        QMessageBox.information(self, "Success", f"Files created:\n{robots_path}\n{sitemap_path}")
        self.status_label.setText(f"Generated robots.txt and sitemap.xml in {self.project_root}")
