"""
Aether Logs Tab – Complete history of all operations
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDateTimeEdit, QMessageBox, QLineEdit, QGroupBox
)
from PySide6.QtCore import Qt, QDateTime, Signal
from PySide6.QtGui import QColor, QFont


class LogsTab(QWidget):
    """Dedicated logs tab showing all operations"""
    
    log_added = Signal(dict)  # Signal to notify dashboard
    
    def __init__(self, parent=None, undo_manager=None):
        super().__init__(parent)
        self.undo_manager = undo_manager
        self.log_entries = []
        self.init_ui()
        
        # Connect to undo manager signals
        if self.undo_manager:
            self.undo_manager.operation_recorded.connect(self.add_log_entry)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📋 Operation History")
        header.setFont(QFont("", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Filter controls
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All", "SEO Operations", "Link Operations", 
                                   "Image Operations", "Backup", "Formatting", "Settings"])
        self.filter_type.currentTextChanged.connect(self.apply_filters)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search logs...")
        self.search_box.textChanged.connect(self.apply_filters)
        
        self.clear_btn = QPushButton("🗑️ Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.apply_filters)
        
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.filter_type)
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_box)
        filter_layout.addWidget(self.clear_btn)
        filter_layout.addWidget(self.refresh_btn)
        filter_layout.addStretch()
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Time", "Type", "Operation", "Details", "Status"])
        self.log_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.log_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.log_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setSortingEnabled(True)
        
        layout.addWidget(self.log_table)
        
        # Status bar
        self.status_label = QLabel("Ready - 0 logs recorded")
        layout.addWidget(self.status_label)
        
        # Add some demo logs
        self.add_demo_logs()
    
    def add_log_entry(self, message, log_type="info", details=""):
        """Add a new log entry"""
        from datetime import datetime
        
        # Determine category
        category = "General"
        if "SEO" in message or "meta" in message.lower():
            category = "SEO Operations"
        elif "link" in message.lower():
            category = "Link Operations"
        elif "image" in message.lower() or "webp" in message.lower():
            category = "Image Operations"
        elif "backup" in message.lower():
            category = "Backup"
        elif "format" in message.lower():
            category = "Formatting"
        
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": category,
            "operation": message[:50],
            "details": details[:200] if details else message,
            "status": "✅ Success" if "✓" in message else "ℹ️ Info",
            "raw_message": message
        }
        
        self.log_entries.insert(0, entry)  # Newest first
        self.apply_filters()
        
        # Emit signal for dashboard
        self.log_added.emit(entry)
        
        # Limit log size
        if len(self.log_entries) > 500:
            self.log_entries = self.log_entries[:500]
    
    def add_demo_logs(self):
        """Add demonstration logs (in real use, these come from operations)"""
        self.add_log_entry("Welcome to Aether! Ready to optimize your project.", "info")
        self.add_log_entry("Project setup wizard completed", "success")
        self.add_log_entry("SEO score analysis completed for 45 pages", "info")
        self.add_log_entry("Found 12 broken links across 3 files", "warning")
    
    def apply_filters(self):
        """Apply filters to the log table"""
        self.log_table.setRowCount(0)
        
        filter_text = self.filter_type.currentText()
        search_text = self.search_box.text().lower()
        
        filtered = []
        for entry in self.log_entries:
            # Apply type filter
            if filter_text != "All" and entry["type"] != filter_text:
                continue
            
            # Apply search filter
            if search_text:
                if (search_text not in entry["operation"].lower() and 
                    search_text not in entry["details"].lower()):
                    continue
            
            filtered.append(entry)
        
        # Populate table
        for row, entry in enumerate(filtered):
            self.log_table.insertRow(row)
            
            # Time
            time_item = QTableWidgetItem(entry["timestamp"])
            time_item.setToolTip(entry["date"])
            self.log_table.setItem(row, 0, time_item)
            
            # Type
            type_item = QTableWidgetItem(entry["type"])
            self.log_table.setItem(row, 1, type_item)
            
            # Operation
            op_item = QTableWidgetItem(entry["operation"])
            self.log_table.setItem(row, 2, op_item)
            
            # Details
            details_item = QTableWidgetItem(entry["details"])
            self.log_table.setItem(row, 3, details_item)
            
            # Status
            status_item = QTableWidgetItem(entry["status"])
            if "✅" in entry["status"]:
                status_item.setForeground(QColor(76, 175, 80))
            elif "⚠️" in entry["status"]:
                status_item.setForeground(QColor(255, 193, 7))
            elif "❌" in entry["status"]:
                status_item.setForeground(QColor(244, 67, 54))
            self.log_table.setItem(row, 4, status_item)
        
        self.status_label.setText(f"Showing {len(filtered)} logs (total: {len(self.log_entries)})")
    
    def clear_logs(self):
        """Clear all logs after confirmation"""
        reply = QMessageBox.question(self, "Clear Logs", 
            "Are you sure you want to clear all logs?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.log_entries = []
            self.log_table.setRowCount(0)
            self.status_label.setText("Logs cleared")
            self.add_log_entry("Logs cleared by user", "info")
    
    def export_logs(self):
        """Export logs to CSV file"""
        from PySide6.QtWidgets import QFileDialog
        import csv
        
        path, _ = QFileDialog.getSaveFileName(self, "Export Logs", "logs.csv", "CSV Files (*.csv)")
        if path:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Time", "Type", "Operation", "Details", "Status"])
                for entry in self.log_entries:
                    writer.writerow([
                        entry["date"],
                        entry["timestamp"],
                        entry["type"],
                        entry["operation"],
                        entry["details"],
                        entry["status"]
                    ])
            QMessageBox.information(self, "Export Complete", f"Logs exported to:\n{path}")
    
    def get_recent_logs(self, limit=10):
        """Get recent logs for dashboard"""
        return self.log_entries[:limit]
    
    def update_theme(self, is_dark):
        """Update theme colors"""
        if is_dark:
            self.log_table.setStyleSheet("""
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
            self.log_table.setStyleSheet("""
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
