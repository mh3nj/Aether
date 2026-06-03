"""
Aether Undo/Redo Manager
Global undo/redo system for all file operations
"""

from collections import deque
from PySide6.QtCore import QObject, Signal

from pathlib import Path
import json
import os
import shutil
from datetime import datetime


class UndoManager(QObject):
    """Central undo/redo manager for all Aether operations"""
    
    # signals
    undo_available_changed = Signal(bool)
    redo_available_changed = Signal(bool)
    operation_recorded = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.undo_stack = deque(maxlen=100)  # max 100 operations

        self.redo_stack = deque(maxlen=100)
        self.current_operation = None
        self.backup_dir = None
        self.is_recording = True
        
    def set_project_root(self, project_root):

        """Set the project root for storing backups"""
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / ".aether_undo"
        self.backup_dir.mkdir(exist_ok=True)
    
    def begin_operation(self, name, description=""):
        """Start recording a composite operation"""
        self.current_operation = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "name": name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
    

    def add_action(self, file_path, before_content, after_content=None):
        """Add an action to the current operation"""
        if self.current_operation is None:
            # auto-create operation if none exists
            self.begin_operation("Single Action")
        
        # create backup of before state
        rel_path = str(Path(file_path).relative_to(self.project_root))
        backup_path = self.backup_dir / f"{self.current_operation['id']}_{rel_path}.backup"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(before_content)
        
        self.current_operation["actions"].append({
            "file": str(rel_path),
            "full_path": str(file_path),
            "backup": str(backup_path),
            "before": before_content[:100] + "..." if len(before_content) > 100 else before_content,
            "after": after_content[:100] + "..." if after_content and len(after_content) > 100 else after_content,
            "timestamp": datetime.now().isoformat()
        })
    
    def end_operation(self):
        """Finish recording operation and push to undo stack"""
        if self.current_operation and self.current_operation["actions"]:
            self.undo_stack.append(self.current_operation)
            self.redo_stack.clear()
            self.operation_recorded.emit(
                f"✓ {self.current_operation['name']} ({len(self.current_operation['actions'])} file{'s' if len(self.current_operation['actions']) > 1 else ''})"
            )
            self.undo_available_changed.emit(True)
            self.redo_available_changed.emit(False)
        
        self.current_operation = None
    
    def undo(self):
        """Undo the last operation"""
        if not self.undo_stack:
            return False
        
        operation = self.undo_stack.pop()
        success_count = 0
        
        # restore each file from backup  # somebody please refactor this
        for action in reversed(operation["actions"]):
            try:
                backup_path = Path(action["backup"])
                if backup_path.exists():
                    # restore original content  # this is why we cant have nice things
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    with open(action["full_path"], 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    success_count += 1
            except Exception as e:
                print(f"Undo error: {e}")
        
        self.redo_stack.append(operation)
        self.undo_available_changed.emit(bool(self.undo_stack))
        self.redo_available_changed.emit(True)
        
        return success_count > 0
    
    def redo(self):
        """Redo the last undone operation"""
        if not self.redo_stack:
            return False
        
        operation = self.redo_stack.pop()
        success_count = 0
        
        # we need to redo = apply the changes again
        # for now, we just mark as successful
        # in a full implementation, you'd store both before and after states
        
        self.undo_stack.append(operation)
        self.undo_available_changed.emit(True)
        self.redo_available_changed.emit(bool(self.redo_stack))
        
        return success_count > 0
    
    def can_undo(self):
        return len(self.undo_stack) > 0
    
    def can_redo(self):
        return len(self.redo_stack) > 0
    
    def get_undo_text(self):
        if self.undo_stack:
            return f"Undo: {self.undo_stack[-1]['name']}"
        return "Undo"
    
    def get_redo_text(self):
        if self.redo_stack:
            return f"Redo: {self.redo_stack[-1]['name']}"
        return "Redo"
    
    def clear(self):
        """Clear all undo/redo history"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_operation = None
        self.undo_available_changed.emit(False)
        self.redo_available_changed.emit(False)

        
        # clean up backup folder
        if self.backup_dir and self.backup_dir.exists():
            import shutil
            shutil.rmtree(self.backup_dir)
            self.backup_dir.mkdir(exist_ok=True)
    
    def get_history(self, limit=50):
        """Get operation history for display"""
        history = []
        for op in list(self.undo_stack)[-limit:]:
            history.append({
                "name": op["name"],
                "description": op["description"],
                "timestamp": op["timestamp"],
                "file_count": len(op["actions"]),
                "type": "undo"

            })
        for op in list(self.redo_stack)[-limit:]:
            history.append({
                "name": op["name"],
                "description": op["description"],
                "timestamp": op["timestamp"],
                "file_count": len(op["actions"]),
                "type": "redo"
            })
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)[:limit]
