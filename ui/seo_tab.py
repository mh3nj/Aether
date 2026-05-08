import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QTreeView, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QMessageBox, QLabel, QDialog,
    QFileDialog, QPlainTextEdit, QFileSystemModel, QApplication, QGroupBox,
    QCheckBox, QScrollArea
)
from PySide6.QtCore import QDir, Qt
from bs4 import BeautifulSoup


class SEOTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.soup = None
        self.init_ui()

    def init_ui(self):
        # Set transparent background for theme inheritance
        self.setStyleSheet("background-color: transparent;")
        
        main_layout = QHBoxLayout(self)

        # Left: file tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.tree = QTreeView()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(str(Path.home())))
        self.tree.clicked.connect(self.on_file_clicked)
        left_layout.addWidget(self.tree)
        main_layout.addWidget(left_widget, 1)

        # Right: scrollable editor
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        right_layout = QVBoxLayout(scroll_widget)
        right_layout.setSpacing(10)

        # ========== BASIC META TAGS ==========
        basic_group = QGroupBox("\uf31c Basic Meta Tags")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        basic_layout = QFormLayout(basic_group)

        self.title_edit = QLineEdit()
        self.title_edit.textChanged.connect(self.update_title_counter)
        basic_layout.addRow("Title:", self.title_edit)

        self.title_counter = QLabel("0 / 50-60 chars")
        self.title_counter.setStyleSheet("color: #8095AB; font-size: 10px;")
        basic_layout.addRow("", self.title_counter)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.textChanged.connect(self.update_desc_counter)
        basic_layout.addRow("Description:", self.desc_edit)

        self.desc_counter = QLabel("0 / 150-160 chars")
        self.desc_counter.setStyleSheet("color: #8095AB; font-size: 10px;")
        basic_layout.addRow("", self.desc_counter)

        self.robots_combo = QComboBox()
        self.robots_combo.addItems(["index, follow", "noindex, follow", "index, nofollow", "noindex, nofollow"])
        basic_layout.addRow("Robots:", self.robots_combo)

        self.canonical_edit = QLineEdit()
        basic_layout.addRow("Canonical URL:", self.canonical_edit)

        right_layout.addWidget(basic_group)

        # ========== OPEN GRAPH ==========
        og_group = QGroupBox("📱 Open Graph (Facebook/LinkedIn)")
        og_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        og_layout = QFormLayout(og_group)

        self.og_title = QLineEdit()
        og_layout.addRow("OG Title:", self.og_title)
        self.og_desc = QTextEdit()
        self.og_desc.setMaximumHeight(60)
        og_layout.addRow("OG Description:", self.og_desc)
        self.og_image = QLineEdit()
        og_layout.addRow("OG Image URL:", self.og_image)
        self.og_url = QLineEdit()
        og_layout.addRow("OG URL:", self.og_url)
        self.og_type = QLineEdit()
        self.og_type.setPlaceholderText("website, article, product")
        og_layout.addRow("OG Type:", self.og_type)
        self.og_locale = QLineEdit()
        self.og_locale.setPlaceholderText("en_US, fa_IR")
        og_layout.addRow("OG Locale:", self.og_locale)
        self.og_site_name = QLineEdit()
        og_layout.addRow("OG Site Name:", self.og_site_name)

        right_layout.addWidget(og_group)

        # ========== TWITTER CARD ==========
        tw_group = QGroupBox("\uf099 Twitter Card")
        tw_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        tw_layout = QFormLayout(tw_group)

        self.tw_card = QComboBox()
        self.tw_card.addItems(["summary", "summary_large_image", "app", "player"])
        tw_layout.addRow("Card Type:", self.tw_card)
        self.tw_title = QLineEdit()
        tw_layout.addRow("Twitter Title:", self.tw_title)
        self.tw_desc = QTextEdit()
        self.tw_desc.setMaximumHeight(60)
        tw_layout.addRow("Twitter Description:", self.tw_desc)
        self.tw_image = QLineEdit()
        tw_layout.addRow("Twitter Image:", self.tw_image)
        self.tw_site = QLineEdit()
        self.tw_site.setPlaceholderText("@YourHandle")
        tw_layout.addRow("Twitter Site:", self.tw_site)
        self.tw_creator = QLineEdit()
        self.tw_creator.setPlaceholderText("@AuthorHandle")
        tw_layout.addRow("Twitter Creator:", self.tw_creator)

        right_layout.addWidget(tw_group)

        # ========== PWA & MOBILE ==========
        pwa_group = QGroupBox("📱 PWA & Mobile Meta")
        pwa_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        pwa_layout = QFormLayout(pwa_group)

        self.theme_color = QLineEdit()
        self.theme_color.setPlaceholderText("#000000 or #ffffff")
        pwa_layout.addRow("Theme Color:", self.theme_color)
        self.color_scheme = QComboBox()
        self.color_scheme.addItems(["light dark", "light", "dark", "only light"])
        pwa_layout.addRow("Color Scheme:", self.color_scheme)
        self.app_capable = QCheckBox("Enable Apple iOS fullscreen mode")
        pwa_layout.addRow("apple-mobile-web-app-capable:", self.app_capable)
        self.status_bar_style = QComboBox()
        self.status_bar_style.addItems(["default", "black", "black-translucent"])
        pwa_layout.addRow("iOS Status Bar Style:", self.status_bar_style)
        self.manifest_url = QLineEdit()
        self.manifest_url.setPlaceholderText("/site.webmanifest")
        pwa_layout.addRow("Web Manifest URL:", self.manifest_url)

        right_layout.addWidget(pwa_group)

        # ========== VERIFICATION ==========
        verify_group = QGroupBox("\uf023 Search Console Verification")
        verify_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        verify_layout = QFormLayout(verify_group)

        self.google_verify = QLineEdit()
        self.google_verify.setPlaceholderText("google-site-verification token")
        verify_layout.addRow("Google:", self.google_verify)
        self.bing_verify = QLineEdit()
        self.bing_verify.setPlaceholderText("bing-verification token")
        verify_layout.addRow("Bing:", self.bing_verify)
        self.yandex_verify = QLineEdit()
        self.yandex_verify.setPlaceholderText("yandex-verification token")
        verify_layout.addRow("Yandex:", self.yandex_verify)

        right_layout.addWidget(verify_group)

        # ========== ADVANCED ==========
        adv_group = QGroupBox("\uf013 Advanced")
        adv_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        adv_layout = QFormLayout(adv_group)

        self.author_edit = QLineEdit()
        adv_layout.addRow("Author:", self.author_edit)
        self.content_language = QLineEdit()
        self.content_language.setPlaceholderText("en")
        adv_layout.addRow("Content-Language:", self.content_language)
        self.noscript_check = QCheckBox("Add noscript fallback (for users without JS)")
        adv_layout.addRow(self.noscript_check)

        right_layout.addWidget(adv_group)

        # ========== BUTTONS ==========
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("\uf00c Apply Meta Tags")
        self.apply_btn.clicked.connect(self.apply_meta)
        self.preset_404_btn = QPushButton("\ue4eb Set as 404 Page (noindex)")
        self.preset_404_btn.clicked.connect(self.apply_404_preset)
        self.hreflang_btn = QPushButton("\uf0ac Generate Hreflang Tags")
        self.hreflang_btn.clicked.connect(self.open_hreflang_dialog)
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.preset_404_btn)
        btn_layout.addWidget(self.hreflang_btn)
        right_layout.addLayout(btn_layout)

        self.status_label = QLabel("Select an HTML file from the left")
        right_layout.addWidget(self.status_label)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 2)

    def update_title_counter(self):
        text = self.title_edit.text()
        length = len(text)
        if length < 50:
            color = "orange"
            tip = "\uf071 Too short (50-60 chars recommended)"
        elif 50 <= length <= 60:
            color = "green"
            tip = "\uf00c Perfect! (50-60 chars)"
        elif 61 <= length <= 70:
            color = "orange"
            tip = "\uf071 Slightly long (50-60 chars is better)"
        else:
            color = "red"
            tip = "\58 Too long! Google may truncate after 60 chars"
        self.title_counter.setText(f"{length} chars - {tip}")
        self.title_counter.setStyleSheet(f"color: {color}; font-size: 10px;")

    def update_desc_counter(self):
        text = self.desc_edit.toPlainText()
        length = len(text)
        if length < 120:
            color = "orange"
            tip = "\uf071 Too short (150-160 chars recommended)"
        elif 120 <= length <= 160:
            color = "green"
            tip = "\uf00c Good range (120-160 chars works well)"
        elif 161 <= length <= 200:
            color = "orange"
            tip = "\uf071 Slightly long (160 chars is ideal for desktop)"
        else:
            color = "red"
            tip = "\58 Too long! Mobile search truncates after ~160 chars"
        self.desc_counter.setText(f"{length} chars - {tip}")
        self.desc_counter.setStyleSheet(f"color: {color}; font-size: 10px;")

    def on_file_clicked(self, index):
        path = self.model.filePath(index)
        if path.lower().endswith(".html") and os.path.isfile(path):
            self.current_file = path
            self.load_meta_from_file()
            self.status_label.setText(f"Loaded: {path}")

    def load_meta_from_file(self):
        with open(self.current_file, 'r', encoding='utf-8') as f:
            html = f.read()
        self.soup = BeautifulSoup(html, 'html.parser')

        title_tag = self.soup.find("title")
        self.title_edit.setText(title_tag.string if title_tag else "")
        self.update_title_counter()

        meta_desc = self.soup.find("meta", attrs={"name": "description"})
        self.desc_edit.setPlainText(meta_desc.get("content", "") if meta_desc else "")
        self.update_desc_counter()

        meta_robots = self.soup.find("meta", attrs={"name": "robots"})
        robots_val = meta_robots.get("content", "index, follow") if meta_robots else "index, follow"
        self.robots_combo.setCurrentText(robots_val)

        canonical = self.soup.find("link", attrs={"rel": "canonical"})
        self.canonical_edit.setText(canonical.get("href", "") if canonical else "")

        self.og_title.setText(self.get_meta_content("og:title") or "")
        self.og_desc.setPlainText(self.get_meta_content("og:description") or "")
        self.og_image.setText(self.get_meta_content("og:image") or "")
        self.og_url.setText(self.get_meta_content("og:url") or "")
        self.og_type.setText(self.get_meta_content("og:type") or "")
        self.og_locale.setText(self.get_meta_content("og:locale") or "")
        self.og_site_name.setText(self.get_meta_content("og:site_name") or "")

        self.tw_card.setCurrentText(self.get_meta_content("twitter:card") or "summary_large_image")
        self.tw_title.setText(self.get_meta_content("twitter:title") or "")
        self.tw_desc.setPlainText(self.get_meta_content("twitter:description") or "")
        self.tw_image.setText(self.get_meta_content("twitter:image") or "")
        self.tw_site.setText(self.get_meta_content("twitter:site") or "")
        self.tw_creator.setText(self.get_meta_content("twitter:creator") or "")

        self.theme_color.setText(self.get_meta_content("theme-color") or "")
        color_scheme_meta = self.soup.find("meta", attrs={"name": "color-scheme"})
        if color_scheme_meta:
            self.color_scheme.setCurrentText(color_scheme_meta.get("content", "light dark"))
        self.app_capable.setChecked(bool(self.soup.find("meta", attrs={"name": "apple-mobile-web-app-capable"})))
        status_style = self.soup.find("meta", attrs={"name": "apple-mobile-web-app-status-bar-style"})
        if status_style:
            self.status_bar_style.setCurrentText(status_style.get("content", "default"))
        manifest = self.soup.find("link", attrs={"rel": "manifest"})
        self.manifest_url.setText(manifest.get("href", "") if manifest else "")

        self.google_verify.setText(self.get_meta_content("google-site-verification") or "")
        self.bing_verify.setText(self.get_meta_content("msvalidate.01") or "")
        self.yandex_verify.setText(self.get_meta_content("yandex-verification") or "")

        self.author_edit.setText(self.get_meta_content("author") or "")
        content_lang = self.soup.find("meta", attrs={"http-equiv": "Content-Language"})
        self.content_language.setText(content_lang.get("content", "") if content_lang else "")

    def get_meta_content(self, name_or_property):
        meta = self.soup.find("meta", attrs={"name": name_or_property})
        if not meta:
            meta = self.soup.find("meta", attrs={"property": name_or_property})
        return meta.get("content", "") if meta else ""

    def apply_meta(self):
        if not self.soup or not self.current_file:
            QMessageBox.warning(self, "Warning", "No HTML file loaded")
            return

        head = self.soup.head
        if not head:
            head = self.soup.new_tag("head")
            self.soup.html.insert(0, head)

        def set_meta(attr_type, attr_value, content):
            if not content:
                return
            existing = self.soup.find("meta", attrs={attr_type: attr_value})
            if existing:
                existing["content"] = content
            else:
                tag = self.soup.new_tag("meta")
                tag[attr_type] = attr_value
                tag["content"] = content
                head.append(tag)

        def set_link(rel, href):
            if not href:
                return
            existing = self.soup.find("link", attrs={"rel": rel})
            if existing:
                existing["href"] = href
            else:
                tag = self.soup.new_tag("link", rel=rel, href=href)
                head.append(tag)

        title_tag = self.soup.find("title")
        if title_tag:
            title_tag.string = self.title_edit.text()
        else:
            new_title = self.soup.new_tag("title")
            new_title.string = self.title_edit.text()
            head.append(new_title)

        set_meta("name", "description", self.desc_edit.toPlainText())
        set_meta("name", "robots", self.robots_combo.currentText())
        set_link("canonical", self.canonical_edit.text())

        set_meta("property", "og:title", self.og_title.text())
        set_meta("property", "og:description", self.og_desc.toPlainText())
        set_meta("property", "og:image", self.og_image.text())
        set_meta("property", "og:url", self.og_url.text())
        set_meta("property", "og:type", self.og_type.text())
        set_meta("property", "og:locale", self.og_locale.text())
        set_meta("property", "og:site_name", self.og_site_name.text())

        set_meta("name", "twitter:card", self.tw_card.currentText())
        set_meta("name", "twitter:title", self.tw_title.text())
        set_meta("name", "twitter:description", self.tw_desc.toPlainText())
        set_meta("name", "twitter:image", self.tw_image.text())
        set_meta("name", "twitter:site", self.tw_site.text())
        set_meta("name", "twitter:creator", self.tw_creator.text())

        set_meta("name", "theme-color", self.theme_color.text())
        set_meta("name", "color-scheme", self.color_scheme.currentText())
        set_meta("name", "apple-mobile-web-app-capable", "yes" if self.app_capable.isChecked() else None)
        set_meta("name", "apple-mobile-web-app-status-bar-style", self.status_bar_style.currentText() if self.status_bar_style.currentText() != "default" else None)
        set_link("manifest", self.manifest_url.text())

        set_meta("name", "google-site-verification", self.google_verify.text())
        set_meta("name", "msvalidate.01", self.bing_verify.text())
        set_meta("name", "yandex-verification", self.yandex_verify.text())

        set_meta("name", "author", self.author_edit.text())
        if self.content_language.text():
            existing = self.soup.find("meta", attrs={"http-equiv": "Content-Language"})
            if existing:
                existing["content"] = self.content_language.text()
            else:
                tag = self.soup.new_tag("meta", **{"http-equiv": "Content-Language", "content": self.content_language.text()})
                head.append(tag)

        if self.noscript_check.isChecked() and not self.soup.find("noscript"):
            noscript = self.soup.new_tag("noscript")
            noscript.string = "Your browser does not support JavaScript or it is disabled. Please enable JavaScript for the best experience."
            self.soup.body.append(noscript)

        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(str(self.soup))
        self.status_label.setText(f"Meta tags updated: {self.current_file}")
        QMessageBox.information(self, "Success", "All meta tags written to file.")

    def apply_404_preset(self):
        self.robots_combo.setCurrentText("noindex, follow")
        if not self.title_edit.text():
            self.title_edit.setText("404 - Page Not Found")
        QMessageBox.information(self, "404 Preset", "Robots set to 'noindex, follow'.\nAdjust other tags as needed.")

    def open_hreflang_dialog(self):
        # Simplified version - you can keep your existing hreflang dialog code here
        QMessageBox.information(self, "Hreflang Generator", "This feature will generate hreflang tags for multi-language sites.\n\nSelect multiple HTML files with language variants.\nPattern: about-en.html, about-fa.html, etc.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                    selection-background-color: #8095AB;
                    selection-color: #FFFFFF;
                }
                QGroupBox {
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                    margin-top: 10px;
                    background-color: transparent;
                }
                QGroupBox::title {
                    color: #E8E8E8;
                }
                QLabel {
                    color: #E8E8E8;
                }
                QPushButton {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #8095AB;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: #1E1F22;
                }
                QCheckBox {
                    color: #E8E8E8;
                    spacing: 5px;
                }
                QTreeView {
                    background-color: #2B2D31;
                    color: #E8E8E8;
                    border: 1px solid #3E4045;
                }
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                    selection-background-color: #8095AB;
                    selection-color: white;
                }
                QGroupBox {
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                    margin-top: 10px;
                    background-color: transparent;
                }
                QGroupBox::title {
                    color: #2C3E50;
                }
                QLabel {
                    color: #2C3E50;
                }
                QPushButton {
                    background-color: #E9ECF1;
                    color: #2C3E50;
                    border: 1px solid #8095AB;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: white;
                }
                QCheckBox {
                    color: #2C3E50;
                    spacing: 5px;
                }
                QTreeView {
                    background-color: #FFFFFF;
                    color: #2C3E50;
                    border: 1px solid #D0D7DE;
                }
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
            """)
