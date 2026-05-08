"""
Aether Dashboard – Command Center for All Tools
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QGridLayout, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Property
from PySide6.QtGui import QFont, QPalette, QColor
from ui.data_bridge import DataBridge


class DashboardTab(QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        self._anim_value = 0
        self.has_project = False
        self.init_ui()
        self.start_animations()
        
        # Setup data bridge
        self.data_bridge = DataBridge()
        self.data_bridge.scan_completed.connect(self.on_scan_completed)
        self.data_bridge.issue_fixed.connect(self.on_issue_fixed)

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

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

        # ========== PROJECT STATUS CARD ==========
        self.project_card = QFrame()
        self.project_card.setFrameShape(QFrame.StyledPanel)
        self.project_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        project_layout = QVBoxLayout(self.project_card)
        self.project_status = QLabel("📁 No Project Loaded")
        self.project_status.setFont(QFont("", 12, QFont.Bold))
        self.project_status.setAlignment(Qt.AlignCenter)
        project_layout.addWidget(self.project_status)
        self.project_hint = QLabel("Select a project folder from any tool to see metrics")
        self.project_hint.setAlignment(Qt.AlignCenter)
        self.project_hint.setStyleSheet("color: #8095AB; font-size: 12px;")
        project_layout.addWidget(self.project_hint)
        scroll_layout.addWidget(self.project_card)

        # ========== HEALTH SCORE CARD ==========
        health_card = QFrame()
        health_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        health_layout = QVBoxLayout(health_card)

        health_title = QLabel("📊 OVERALL SEO HEALTH")
        health_title.setFont(QFont("", 14, QFont.Bold))
        health_layout.addWidget(health_title)

        self.score_label = QLabel("--")
        score_font = QFont()
        score_font.setPointSize(48)
        score_font.setBold(True)
        self.score_label.setFont(score_font)
        self.score_label.setAlignment(Qt.AlignCenter)
        health_layout.addWidget(self.score_label)

        self.score_status = QLabel("Select a project folder to begin")
        self.score_status.setAlignment(Qt.AlignCenter)
        health_layout.addWidget(self.score_status)

        self.health_progress = QProgressBar()
        self.health_progress.setValue(0)
        self.health_progress.setTextVisible(False)
        self.health_progress.setFixedHeight(8)
        health_layout.addWidget(self.health_progress)

        scroll_layout.addWidget(health_card)

        # ========== QUICK ACTIONS GRID ==========
        actions_card = QFrame()
        actions_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
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
            actions_grid.addWidget(btn, i // 2, i % 2)

        actions_layout.addLayout(actions_grid)
        scroll_layout.addWidget(actions_card)

        # ========== KEY METRICS ==========
        metrics_card = QFrame()
        metrics_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        metrics_layout = QGridLayout(metrics_card)

        metrics_title = QLabel("📈 KEY METRICS")
        metrics_title.setFont(QFont("", 14, QFont.Bold))
        metrics_layout.addWidget(metrics_title, 0, 0, 1, 2)

        self.metric_widgets = {}
        metrics_data = [
            ("pages_count", "Pages Analyzed", "0", "📄"),
            ("issues_count", "Issues Found", "0", "⚠️"),
            ("avg_score", "Avg SEO Score", "0%", "⭐"),
            ("fixes_count", "Fixes Applied", "0", "✅"),
        ]

        for i, (key, label, value, icon) in enumerate(metrics_data):
            card = QFrame()
            card.setStyleSheet("background-color: rgba(128, 149, 171, 0.15); border-radius: 8px; padding: 10px;")
            card_layout = QVBoxLayout(card)
            val_label = QLabel(f"{icon} {value}")
            val_label.setFont(QFont("", 18, QFont.Bold))
            val_label.setAlignment(Qt.AlignCenter)
            name_label = QLabel(label)
            name_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(val_label)
            card_layout.addWidget(name_label)
            metrics_layout.addWidget(card, 1 + i // 2, i % 2)
            self.metric_widgets[key] = val_label

        scroll_layout.addWidget(metrics_card)

        # ========== TOP ISSUES & RECENT FIXES ==========
        issues_fixes_layout = QHBoxLayout()
        issues_fixes_layout.setSpacing(20)

        issues_card = QFrame()
        issues_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        issues_layout = QVBoxLayout(issues_card)
        issues_title = QLabel("⚠️ TOP ISSUES")
        issues_title.setFont(QFont("", 12, QFont.Bold))
        issues_layout.addWidget(issues_title)

        self.issues_list = QLabel("• No project loaded\n• Select a folder to see issues")
        self.issues_list.setWordWrap(True)
        issues_layout.addWidget(self.issues_list)

        fixes_card = QFrame()
        fixes_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        fixes_layout = QVBoxLayout(fixes_card)
        fixes_title = QLabel("✅ RECENT FIXES")
        fixes_title.setFont(QFont("", 12, QFont.Bold))
        fixes_layout.addWidget(fixes_title)

        self.fixes_list = QLabel("• No fixes yet\n• Apply fixes to see them here")
        self.fixes_list.setWordWrap(True)
        fixes_layout.addWidget(self.fixes_list)

        issues_fixes_layout.addWidget(issues_card)
        issues_fixes_layout.addWidget(fixes_card)
        scroll_layout.addLayout(issues_fixes_layout)

        # ========== QUICK LAUNCH TABS ==========
        tabs_card = QFrame()
        tabs_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
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

        # ========== MINI LOGS VIEWER ==========
        logs_card = QFrame()
        logs_card.setStyleSheet("""
            QFrame {
                background-color: rgba(128, 149, 171, 0.1);
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
        """)
        logs_layout = QVBoxLayout(logs_card)
        logs_title = QLabel("📋 RECENT ACTIVITY")
        logs_title.setFont(QFont("", 12, QFont.Bold))
        logs_layout.addWidget(logs_title)

        self.mini_logs_list = QLabel("• No recent activity")
        self.mini_logs_list.setWordWrap(True)
        self.mini_logs_list.setMaximumHeight(100)
        logs_layout.addWidget(self.mini_logs_list)

        self.view_all_logs_btn = QPushButton("View All Logs →")
        self.view_all_logs_btn.clicked.connect(self.go_to_logs_tab)
        logs_layout.addWidget(self.view_all_logs_btn)

        scroll_layout.addWidget(logs_card)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Footer
        footer = QLabel("💡 Tip: Use Ctrl+1 to return here anytime")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #8095AB; padding: 10px;")
        main_layout.addWidget(footer)

    def on_scan_completed(self, data):
        """Handle scan completion from any tab"""
        self.has_project = True
        self.project_status.setText("📁 Project Loaded")
        self.metric_widgets['pages_count'].setText(f"📄 {data.get('pages', 0)}")
        self.metric_widgets['issues_count'].setText(f"⚠️ {data.get('issues', 0)}")
        
        score = data.get('score', 0)
        if score > 0:
            self.metric_widgets['avg_score'].setText(f"⭐ {score}%")
            self.animation.setEndValue(score)
            self.animation.start()
        
        self.issues_list.setText(f"• Found {data.get('issues', 0)} issues to fix")

    def on_issue_fixed(self, fix_type, count):
        """Handle issue fixes from any tab"""
        current_text = self.metric_widgets['fixes_count'].text()
        current_fixes = int(current_text.replace("✅ ", "")) if "✅" in current_text else 0
        new_fixes = current_fixes + count
        self.metric_widgets['fixes_count'].setText(f"✅ {new_fixes}")
        
        current_fixes_text = self.fixes_list.text()
        if current_fixes_text == "• No fixes yet\n• Apply fixes to see them here":
            self.fixes_list.setText(f"• Fixed {count} {fix_type}(s)")
        else:
            self.fixes_list.setText(f"{current_fixes_text}\n• Fixed {count} {fix_type}(s)")

    def add_log_entry(self, log_entry):
        """Add a log entry to the mini viewer"""
        if hasattr(self, 'mini_logs_list'):
            current_text = self.mini_logs_list.text()
            if current_text == "• No recent activity":
                current_text = ""
            time = log_entry.get('timestamp', '')
            operation = log_entry.get('operation', '')[:60]
            new_entry = f"• {time} - {operation}"
            lines = current_text.split('\n')
            lines.insert(0, new_entry)
            if len(lines) > 5:
                lines = lines[:5]
            self.mini_logs_list.setText('\n'.join(lines))

    def go_to_logs_tab(self):
        """Switch to logs tab"""
        if self.main_window:
            for i in range(self.main_window.tabs.count()):
                if "Logs" in self.main_window.tabs.tabText(i):
                    self.main_window.tabs.setCurrentIndex(i)
                    break

    def start_animations(self):
        self.animation = QPropertyAnimation(self, b"animValue")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self.update_score_display)

    def get_anim_value(self):
        return self._anim_value

    def set_anim_value(self, value):
        self._anim_value = value
        self.score_label.setText(f"{int(value)}%" if value > 0 else "--")

    animValue = Property(int, get_anim_value, set_anim_value)

    def update_score_display(self, value):
        if value <= 0:
            self.score_label.setText("--")
            self.score_status.setText("Select a project folder to begin")
            return
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

    def update_theme(self, is_dark):
        """Update colors when theme changes"""
        if is_dark:
            self.setStyleSheet("""
                QLabel, QPushButton { color: #E8E8E8; }
                QProgressBar::chunk { background-color: #8095AB; }
                QFrame { background-color: rgba(128, 149, 171, 0.1); }
                QPushButton {
                    background-color: #2B2D31;
                    border: 1px solid #8095AB;
                    border-radius: 8px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: #1E1F22;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel, QPushButton { color: #2C3E50; }
                QProgressBar::chunk { background-color: #8095AB; }
                QFrame { background-color: rgba(128, 149, 171, 0.05); }
                QPushButton {
                    background-color: #E9ECF1;
                    border: 1px solid #8095AB;
                    border-radius: 8px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #8095AB;
                    color: white;
                }
            """)

    # Navigation methods
    def go_to_formatter(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(1)

    def go_to_seo(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(2)

    def go_to_media(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(4)

    def go_to_links(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(5)

    def go_to_accessibility(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(6)

    def go_to_backup(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(8)

    def go_to_performance(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(7)

    def go_to_schema(self):
        if self.main_window:
            self.main_window.tabs.setCurrentIndex(3)

    def go_to_tab_by_name(self, name):
        if not self.main_window:
            return
        tab_indexes = {
            "🔍 SEO": 2,
            "🔗 Links": 5,
            "🖼️ Images": 4,
            "💾 Backup": 8,
            "📊 Schema": 3,
        }
        if name in tab_indexes:
            self.main_window.tabs.setCurrentIndex(tab_indexes[name])
