import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
    QGroupBox, QApplication
)
from PySide6.QtCore import Qt


class BackupTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.backup_folder = None
        self.backup_history = []
        self.selected_backup = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Project folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # Backup location display
        backup_row = QHBoxLayout()
        self.backup_label = QLabel("Backup location: (auto-created in project)")
        backup_row.addWidget(self.backup_label)
        backup_row.addStretch()
        layout.addLayout(backup_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.create_btn = QPushButton("\f790 Create Backup Now")
        self.create_btn.clicked.connect(self.create_backup)
        self.create_btn.setEnabled(False)
        self.restore_btn = QPushButton("\f1b8 Restore from Backup")
        self.restore_btn.clicked.connect(self.restore_backup)
        self.restore_btn.setEnabled(False)
        btn_row.addWidget(self.create_btn)
        btn_row.addWidget(self.restore_btn)
        layout.addLayout(btn_row)

        # Backup history list
        history_group = QGroupBox("Backup History")
        history_layout = QVBoxLayout(history_group)
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_selected)
        history_layout.addWidget(self.history_list)
        layout.addWidget(history_group)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Ready - Select a project folder")
        layout.addWidget(self.status_label)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)
            self.backup_folder = Path(path) / ".webdev_backups"
            self.backup_label.setText(f"Backup location: {self.backup_folder}")
            self.load_backup_history()
            self.create_btn.setEnabled(True)

    def load_backup_history(self):
        """Load existing backup history from the project."""
        self.history_list.clear()
        self.backup_history = []
        
        if not self.backup_folder or not self.backup_folder.exists():
            self.restore_btn.setEnabled(False)
            return
        
        # Load manifest if exists
        manifest_path = self.backup_folder / "backup_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self.backup_history = json.load(f)
        
        # Populate list
        for backup in self.backup_history:
            item_text = f"{backup['datetime']} - {backup['file_count']} files, {backup['size_kb']} KB"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, backup)
            self.history_list.addItem(item)
        
        if self.backup_history:
            self.restore_btn.setEnabled(True)
        else:
            self.restore_btn.setEnabled(False)

    def create_backup(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        # Create backup folder
        self.backup_folder.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped backup folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subfolder = self.backup_folder / timestamp
        backup_subfolder.mkdir(parents=True, exist_ok=True)

        # Find all files to backup (HTML, CSS, JS, images, etc.)
        extensions = [".html", ".htm", ".css", ".js", ".py", ".json", ".xml", ".txt", 
                      ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"]
        files_to_backup = []
        for ext in extensions:
            files_to_backup.extend(Path(self.project_folder).rglob(f"*{ext}"))
        
        # Exclude the backup folder itself
        files_to_backup = [f for f in files_to_backup if str(self.backup_folder) not in str(f)]

        self.create_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(files_to_backup))
        self.status_label.setText(f"Backing up {len(files_to_backup)} files...")

        total_size = 0
        for idx, file_path in enumerate(files_to_backup):
            try:
                rel_path = file_path.relative_to(self.project_folder)
                dest_path = backup_subfolder / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_path)
                total_size += file_path.stat().st_size
            except Exception as e:
                self.status_label.setText(f"Error backing up {file_path.name}: {e}")
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        size_kb = total_size // 1024
        # Save to manifest
        backup_info = {
            "timestamp": timestamp,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "file_count": len(files_to_backup),
            "size_kb": size_kb,
            "folder": str(backup_subfolder)
        }
        self.backup_history.insert(0, backup_info)
        
        manifest_path = self.backup_folder / "backup_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.backup_history, f, indent=2)

        self.load_backup_history()
        self.progress.setVisible(False)
        self.create_btn.setEnabled(True)
        self.status_label.setText(f"\f00c Backup complete! {len(files_to_backup)} files backed up.")
        QMessageBox.information(self, "Backup Complete", 
                                f"Backed up {len(files_to_backup)} files ({size_kb} KB)\n"
                                f"Location: {backup_subfolder}")

    def on_history_selected(self, item):
        self.selected_backup = item.data(Qt.UserRole)

    def restore_backup(self):
        if not self.selected_backup:
            QMessageBox.warning(self, "Warning", "Select a backup from the list first.")
            return

        reply = QMessageBox.question(self, "Confirm Restore",
                                     f"Restore backup from {self.selected_backup['datetime']}?\n\n"
                                     f"This will OVERWRITE {self.selected_backup['file_count']} files in your project.\n"
                                     f"Current changes will be lost.\n\n"
                                     f"Are you sure?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return

        backup_folder = Path(self.selected_backup['folder'])
        if not backup_folder.exists():
            QMessageBox.warning(self, "Error", "Backup folder not found.")
            return

        self.restore_btn.setEnabled(False)
        self.progress.setVisible(True)
        
        # Count files to restore
        files_to_restore = list(backup_folder.rglob("*"))
        files_to_restore = [f for f in files_to_restore if f.is_file()]
        self.progress.setMaximum(len(files_to_restore))

        restored = 0
        for idx, backup_file in enumerate(files_to_restore):
            try:
                rel_path = backup_file.relative_to(backup_folder)
                dest_path = Path(self.project_folder) / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, dest_path)
                restored += 1
            except Exception as e:
                self.status_label.setText(f"Error restoring: {e}")
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.restore_btn.setEnabled(True)
        self.status_label.setText(f"\f00c Restored {restored} files from backup.")
        QMessageBox.information(self, "Restore Complete", 
                                f"Restored {restored} files.\nYour project has been reverted.")

    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        pass
