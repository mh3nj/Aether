"""
Aether Data Bridge – Communication between tabs and dashboard
"""

from PySide6.QtCore import QObject, Signal


class DataBridge(QObject):
    """Central communication hub for tab data"""
    
    # Signals for different data types
    scan_completed = Signal(dict)  # When a scan finishes
    issue_fixed = Signal(str, int)  # When an issue is fixed (type, count)
    metrics_updated = Signal(dict)  # General metrics update
    
    def __init__(self):
        super().__init__()
        self.metrics = {
            "pages_analyzed": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "seo_score": 0,
            "last_scan": None
        }
    
    def report_scan(self, file_count, issue_count, score=0):
        """Report a scan completion from any tab"""
        self.metrics["pages_analyzed"] = file_count
        self.metrics["issues_found"] = issue_count
        self.metrics["seo_score"] = score if score > 0 else self.metrics["seo_score"]
        self.metrics["last_scan"] = __import__('datetime').datetime.now().isoformat()
        
        self.scan_completed.emit({
            "pages": self.metrics["pages_analyzed"],
            "issues": self.metrics["issues_found"],
            "score": self.metrics["seo_score"],
            "timestamp": self.metrics["last_scan"]
        })
    
    def report_fix(self, fix_type, count=1):
        """Report when issues are fixed"""
        self.metrics["issues_fixed"] += count
        self.issue_fixed.emit(fix_type, count)
        self.metrics_updated.emit({"fixes": self.metrics["issues_fixed"]})
