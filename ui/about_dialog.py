"""
Aether About Dialog
"""

import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.setWindowTitle("About Aether")
        self.setModal(True)
        self.resize(500, 450)
        
        layout = QVBoxLayout(self)
        
        # logo
        if is_dark:
            logo_path = "assets/logos/aether-full-dark.png"
        else:
            logo_path = "assets/logos/aether-full-light.png"
        
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)

            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        
        # title
        title = QLabel("Aether Web Dev Tools")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # version  # somebody please refactor this
        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # description
        desc = QLabel(
            "A complete toolkit for web developers and SEO specialists.\n\n"
            "28 powerful tools in one offline application:\n"
            "• Code Formatting • SEO Optimization • Favicon Generator\n"
            "• Schema Library • Lazy Loading • OG Preview\n"
            "• Accessibility Checker • Link Manager • WebP Converter\n"
            "• Security (CSP/SRI) • Performance Optimizer • And 17 more!\n\n"
            "© 2026 Mohsen Jafari (Parsegan)\n"
            "parsegan@proton.me"
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
