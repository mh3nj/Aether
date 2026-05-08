"""
Aether Dashboard – Command Center for All Tools
Quick stats, health score, and one-click access to everything
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QGridLayout, QScrollArea, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QFont, QPalette, QColor


class DashboardTab(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self.init_ui()
        self.start_animations()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)

        # Scroll area for dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # ========== HEADER ==========
        header = QLabel("🌌 AETHER DASHBOARD")
        header_font = QFont()
        header_font.setPointSize(24)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(header)

        # Stats line
        stats_line = QLabel("Your complete web development command center")
        stats_line.setAlignment(Qt.AlignCenter)
        stats_line.setStyleSheet("color: #8095AB; font-size: 14px;")
        scroll_layout.addWidget(stats_line)

        # ========== HEALTH SCORE CARD ==========
        health_card = self.create_card()
        health_layout = QVBoxLayout(health_card)

        health_title = QLabel("📊 OVERALL SEO HEALTH")
        health_title.setFont(QFont("", 14, QFont.Bold))
        health_layout.addWidget(health_title)

        # Score circle (simulated for now)
        self.score_label = QLabel("78%")
        score_font = QFont()
        score_font.setPointSize(48)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("color: #4CAF50;")
        health_layout.addWidget(self.score_label)

        self.score_status = QLabel("Good! Keep optimizing.")
        self.score_status.setAlignment(Qt.AlignCenter)
        health_layout.addWidget(self.score_status)

        # Progress ring style
        self.health_progress = QProgressBar()
        self.health_progress.setValue(78)
        self.health_progress.setTextVisible(False)
        self.health_progress.setFixedHeight(8)
        health_layout.addWidget(self.health_progress)

        scroll_layout.addWidget(health_card)

        # ========== QUICK ACTIONS GRID ==========
        actions_card = self.create_card()
        actions_layout = QVBoxLayout(actions_card)

        actions_title = QLabel("🎯 QUICK ACTIONS")
        actions_title.setFont(QFont("", 14, QFont.Bold))
        actions_layout.addWidget(actions_title)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(10)

        quick_actions = [
            ("📝 Format Code", "Ctrl+2", self.go_to_formatter),
            ("🔍 SEO Check", "Ctrl+3", self.go_to_seo),
            ("🖼️ Optimize Images", "Ctrl+5", self.go_to_media),
            ("🔗 Fix Broken Links", "Ctrl+6", self.go_to_links),
            ("♿ Accessibility", "Ctrl+7", self.go_to_accessibility),
            ("💾 Backup Project", "Ctrl+9", self.go_to_backup),
            ("⚡ Performance", "Ctrl+8", self.go_to_performance),
            ("📊 Schema", "Ctrl+4", self.go_to_schema),
        ]

        for i, (name, shortcut, callback) in enumerate(quick_actions):
            btn = QPushButton(f"{name}\n{shortcut}")
            btn.setMinimumHeight(70)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 10px;
                    border: 1px solid #8095AB;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: white;
                }
            """)
            actions_grid.addWidget(btn, i // 2, i % 2)

        actions_layout.addLayout(actions_grid)
        scroll_layout.addWidget(actions_card)

        # ========== KEY METRICS ==========
        metrics_card = self.create_card()
        metrics_layout = QGridLayout(metrics_card)

        metrics_title = QLabel("📈 KEY METRICS")
        metrics_title.setFont(QFont("", 14, QFont.Bold))
        metrics_layout.addWidget(metrics_title, 0, 0, 1, 2)

        metrics_data = [
            ("Pages Analyzed", "0", "📄"),
            ("Issues Found", "0", "⚠️"),
            ("Avg SEO Score", "0%", "⭐"),
            ("Fixes Applied", "0", "✅"),
        ]

        for i, (label, value, icon) in enumerate(metrics_data):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: rgba(128, 149, 171, 0.1);
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            card_layout = QVBoxLayout(card)
            val_label = QLabel(f"{icon} {value}")
            val_label.setFont(QFont("", 18, QFont.Bold))
            val_label.setAlignment(Qt.AlignCenter)
            name_label = QLabel(label)
            name_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(val_label)
            card_layout.addWidget(name_label)
            metrics_layout.addWidget(card, 1 + i // 2, i % 2)

        scroll_layout.addWidget(metrics_card)

        # ========== TOP ISSUES & RECENT FIXES ==========
        issues_fixes_layout = QHBoxLayout()
        issues_fixes_layout.setSpacing(20)

        # Top Issues
        issues_card = self.create_card()
        issues_layout = QVBoxLayout(issues_card)
        issues_title = QLabel("⚠️ TOP ISSUES")
        issues_title.setFont(QFont("", 12, QFont.Bold))
        issues_layout.addWidget(issues_title)

        self.issues_list = QLabel("• No data yet\nRun a scan to see issues")
        self.issues_list.setWordWrap(True)
        issues_layout.addWidget(self.issues_list)

        # Recent Fixes
        fixes_card = self.create_card()
        fixes_layout = QVBoxLayout(fixes_card)
        fixes_title = QLabel("✅ RECENT FIXES")
        fixes_title.setFont(QFont("", 12, QFont.Bold))
        fixes_layout.addWidget(fixes_title)

        self.fixes_list = QLabel("• No fixes yet\nApply fixes to see them here")
        self.fixes_list.setWordWrap(True)
        fixes_layout.addWidget(self.fixes_list)

        issues_fixes_layout.addWidget(issues_card)
        issues_fixes_layout.addWidget(fixes_card)
        scroll_layout.addLayout(issues_fixes_layout)

        # ========== QUICK LAUNCH TABS ==========
        tabs_card = self.create_card()
        tabs_layout = QVBoxLayout(tabs_card)
        tabs_title = QLabel("🚀 RECENT TABS")
        tabs_title.setFont(QFont("", 12, QFont.Bold))
        tabs_layout.addWidget(tabs_title)

        tabs_grid = QHBoxLayout()
        recent_tabs = ["🔍 SEO", "🔗 Links", "🖼️ Images", "💾 Backup", "📊 Schema"]
        for tab_name in recent_tabs:
            btn = QPushButton(tab_name)
            btn.clicked.connect(lambda checked, t=tab_name: self.go_to_tab_by_name(t))
            tabs_grid.addWidget(btn)

        tabs_layout.addLayout(tabs_grid)
        scroll_layout.addWidget(tabs_card)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Footer
        footer = QLabel("💡 Tip: Use Ctrl+1 to return here anytime")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #8095AB; padding: 10px;")
        main_layout.addWidget(footer)

    def create_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.05);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        return card

    def start_animations(self):
        # Animate the health score counting up
        self.anim_value = 0
        self.animation = QPropertyAnimation(self, b"anim_value")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(78)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self.update_score_display)
        QTimer.singleShot(500, self.animation.start)

    def get_anim_value(self):
        return self.anim_value

    def set_anim_value(self, value):
        self.anim_value = value
        self.score_label.setText(f"{int(value)}%")

    anim_value = property(get_anim_value, set_anim_value)

    def update_score_display(self, value):
        self.score_label.setText(f"{int(value)}%")
        if value < 50:
            self.score_label.setStyleSheet("color: #F44336;")
            self.score_status.setText("Poor! Needs immediate attention.")
        elif value < 70:
            self.score_label.setStyleSheet("color: #FFC107;")
            self.score_status.setText("Fair. Room for improvement.")
        else:
            self.score_label.setStyleSheet("color: #4CAF50;")
            self.score_status.setText("Good! Keep optimizing.")

    # Navigation methods
    def go_to_formatter(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(0)

    def go_to_seo(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(1)

    def go_to_media(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(5)

    def go_to_links(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(6)

    def go_to_accessibility(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(12)

    def go_to_backup(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(15)

    def go_to_performance(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(19)

    def go_to_schema(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(7)

    def go_to_tab_by_name(self, name):
        if not self.main_window:
            return
        tab_names = {
            "🔍 SEO": 1,
            "🔗 Links": 6,
            "🖼️ Images": 5,
            "💾 Backup": 15,
            "📊 Schema": 7,
        }
        if name in tab_names:
            self.main_window.tabs.setCurrentIndex(tab_names[name])

    def update_metrics(self, scan_data=None):
        """Update dashboard with real data from scans"""
        # This will be populated as other tabs send data
        pass

    def update_theme(self, is_dark):
        """Update colors when theme changes"""
        if is_dark:
            self.setStyleSheet("""
                QLabel { color: #E8E8E8; }
                QProgressBar::chunk { background-color: #8095AB; }
            """)
        else:
            self.setStyleSheet("""
                QLabel { color: #2C3E50; }
                QProgressBar::chunk { background-color: #8095AB; }
            """)
