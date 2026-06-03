import os
import re
import subprocess
import shutil
import difflib
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QPlainTextEdit,
    QMessageBox,
    QLabel,
    QComboBox,
    QSplitter,
)

from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PySide6.QtCore import Qt
import black
import jsbeautifier


class FormatterTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.parent_window = parent  # to access theme settings if needed  # lol don't ask
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # file operations row
        file_row = QHBoxLayout()
        self.new_btn = QPushButton("\uf15c New / Paste")
        self.new_btn.clicked.connect(self.new_file)
        self.open_btn = QPushButton("\uf07c Open File")
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn = QPushButton("\uf019 Save Left as File...")

        self.save_btn.clicked.connect(self.save_file)
        self.save_as_btn = QPushButton("\uf305 Save Left As...")
        self.save_as_btn.clicked.connect(self.save_as)
        file_row.addWidget(self.new_btn)
        file_row.addWidget(self.open_btn)
        file_row.addWidget(self.save_btn)

        file_row.addWidget(self.save_as_btn)
        file_row.addStretch()
        layout.addLayout(file_row)

        # format controls row
        format_row = QHBoxLayout()
        self.format_btn = QPushButton("\uf53f Format → Right Panel")
        self.format_btn.clicked.connect(self.format_current)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(

            ["Auto Detect", "Python", "JavaScript", "HTML", "CSS", "TypeScript"]
        )
        self.lang_combo.setToolTip("Select language or let Auto Detect guess")
        self.copy_btn = QPushButton("\uf15c Copy Right → Left")
        self.copy_btn.clicked.connect(self.copy_right_to_left)
        format_row.addWidget(self.format_btn)
        format_row.addWidget(QLabel("Language:"))
        format_row.addWidget(self.lang_combo)
        format_row.addWidget(self.copy_btn)
        format_row.addStretch()
        layout.addLayout(format_row)

        # split view: left (before), right (after)
        self.splitter = QSplitter(Qt.Horizontal)
        self.left_editor = QPlainTextEdit()
        self.left_editor.setFont(QFont("Courier New", 10))
        self.left_editor.setPlaceholderText("Original code (left)")
        self.right_editor = QPlainTextEdit()
        self.right_editor.setFont(QFont("Courier New", 10))
        self.right_editor.setPlaceholderText(
            "Formatted code (right) – will show diff highlights"
        )
        self.right_editor.setReadOnly(True)
        self.splitter.addWidget(self.left_editor)
        self.splitter.addWidget(self.right_editor)
        layout.addWidget(self.splitter)

        # status bar
        self.status_label = QLabel("Ready – paste or open file, then click Format")
        layout.addWidget(self.status_label)

    # ------------------------------------------------------------------
    # file ops
    # ------------------------------------------------------------------
    def new_file(self):
        self.current_file = None
        self.left_editor.clear()
        self.right_editor.clear()
        self.status_label.setText(
            "New unsaved buffer – paste your code and click Format"
        )

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Code Files (*.py *.js *.html *.css *.ts *.tsx *.jsx);;All Files (*.*)",
        )
        if path:
            self.current_file = path
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            self.left_editor.setPlainText(code)
            self.right_editor.clear()
            self.status_label.setText(f"Opened: {path}")
            ext = Path(path).suffix.lower()
            if ext == ".py":
                self.lang_combo.setCurrentIndex(1)
            elif ext == ".js":
                self.lang_combo.setCurrentIndex(2)
            elif ext == ".html":
                self.lang_combo.setCurrentIndex(3)
            elif ext == ".css":
                self.lang_combo.setCurrentIndex(4)
            elif ext in (".ts", ".tsx"):
                self.lang_combo.setCurrentIndex(5)

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.left_editor.toPlainText())
            self.status_label.setText(f"Saved: {self.current_file}")
        else:
            self.save_as()

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", "All Files (*.*)")
        if path:
            self.current_file = path
            self.save_file()

    def copy_right_to_left(self):
        """Copy formatted code from right editor to left editor."""
        formatted = self.right_editor.toPlainText()
        if formatted.strip():
            self.left_editor.setPlainText(formatted)
            self.status_label.setText("Copied formatted code to left editor.")
        else:
            QMessageBox.information(
                self, "Info", "Right panel is empty. Format something first."
            )


    # ------------------------------------------------------------------
    # language detection
    # ------------------------------------------------------------------
    def detect_language(self, code):
        code_lower = code.strip().lower()
        if not code_lower:
            return "html"
        if (
            code_lower.startswith("<!doctype")
            or "<html" in code_lower[:200]
            or "<head" in code_lower[:200]
        ):
            return "html"
        if "<style" in code_lower[:200] or "<script" in code_lower[:200]:
            return "html"
        if re.search(r"def\s+\w+\s*\(.*\):", code_lower[:500]):
            return "python"
        if re.search(
            r"function\s+\w+\s*\(|=>|let\s+\w+\s*=|const\s+\w+\s*=", code_lower[:500]
        ):
            return "javascript"
        if re.search(r"{\s*[\w\-]+\s*:\s*[^;]+;?\s*}", code_lower[:300]):
            return "css"
        if re.search(r"interface\s+\w+|:\s*string\b|:\s*number\b", code_lower[:500]):
            return "typescript"
        return "html"

    # ------------------------------------------------------------------
    # formatting with diff highlight
    # ------------------------------------------------------------------
    def format_current(self):
        code = self.left_editor.toPlainText()
        if not code.strip():
            QMessageBox.information(
                self, "Info", "Nothing to format – paste some code first."
            )
            return

        lang_choice = self.lang_combo.currentText()
        if lang_choice == "Auto Detect":
            lang = self.detect_language(code)
        elif lang_choice == "Python":
            lang = "python"
        elif lang_choice == "JavaScript":
            lang = "javascript"
        elif lang_choice == "HTML":
            lang = "html"
        elif lang_choice == "CSS":
            lang = "css"
        elif lang_choice == "TypeScript":
            lang = "typescript"
        else:
            lang = "html"

        # sanity check for html
        if lang == "html":
            open_brackets = code.count("<")
            close_brackets = code.count(">")
            if open_brackets != close_brackets or open_brackets < 2:
                reply = QMessageBox.question(
                    self,

                    "Malformed HTML",
                    f"Angle brackets mismatch: {open_brackets} vs {close_brackets}.\nFormatting may produce garbage.\nProceed?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return
            try:
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(code, "html.parser")
                if not soup.find():
                    reply = QMessageBox.question(
                        self,
                        "No HTML tags",
                        "Parser found no HTML tags.\nProceed?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply == QMessageBox.No:
                        return
            except Exception as e:
                reply = QMessageBox.question(
                    self,
                    "HTML parse error",
                    f"Parser error: {str(e)[:100]}\nProceed?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

        try:
            if lang == "python":
                formatted = black.format_str(code, mode=black.Mode())
            elif lang in ("javascript", "typescript", "html", "css"):
                formatted = self._run_prettier(code, lang)
            else:
                QMessageBox.warning(self, "Info", f"Unsupported language: {lang}")
                return
        except Exception as e:
            QMessageBox.critical(self, "Format Error", str(e))
            return

        if formatted and formatted != code:
            self.right_editor.setPlainText(formatted)
            self.highlight_diff(code, formatted)
            self.status_label.setText(f"Formatted as {lang.upper()}")
        else:
            self.right_editor.setPlainText("No changes detected.")
            self.status_label.setText("Already formatted – no changes")

    def _run_prettier(self, code, lang):
        parser_map = {
            "javascript": "babel",
            "typescript": "typescript",
            "html": "html",
            "css": "css",
        }
        parser = parser_map.get(lang, "html")

        prettier_cmd = shutil.which("prettier") or shutil.which("prettier.cmd")
        if not prettier_cmd:
            prettier_cmd = "npx"
            args = [prettier_cmd, "prettier", f"--parser={parser}", "--stdin"]
        else:
            args = [prettier_cmd, f"--parser={parser}", "--stdin"]

        try:
            result = subprocess.run(
                args,
                input=code,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=15,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
            else:
                return self._jsbeautify_fallback(code, lang)
        except Exception:
            return self._jsbeautify_fallback(code, lang)

    def _jsbeautify_fallback(self, code, lang):
        opts = {
            "indent_size": 2,
            "indent_char": " ",
            "preserve_newlines": True,
            "end_with_newline": False,
        }
        if lang == "html":
            opts["indent_inner_html"] = True
            opts["extra_liners"] = []
            opts["wrap_attributes"] = "auto"
        return jsbeautifier.beautify(code, opts)

    # ------------------------------------------------------------------
    # diff highlighting
    # ------------------------------------------------------------------
    def highlight_diff(self, original, formatted):
        """Compare line by line and highlight differences in the right editor."""

        orig_lines = original.splitlines()
        fmt_lines = formatted.splitlines()

        # use difflib to get opcodes
        matcher = difflib.SequenceMatcher(None, orig_lines, fmt_lines)
        opcodes = matcher.get_opcodes()

        # prepare a list of line numbers (0-index) in fmt that are different (modified or inserted)
        changed_lines = set()
        for tag, i1, i2, j1, j2 in opcodes:
            if tag != "equal":
                for j in range(j1, j2):
                    changed_lines.add(j)

        # apply highlighting to the right editor  # i have no idea what this does
        cursor = self.right_editor.textCursor()
        cursor.select(QTextCursor.Document)

        cursor.setCharFormat(QTextCharFormat())  # reset all formatting
        cursor.clearSelection()

        # determine highlight color based on current theme
        # we can get parent window's theme state
        is_dark = False
        if self.parent_window:
            is_dark = self.parent_window.theme_action.isChecked()
        highlight_color = (
            QColor(255, 255, 180) if not is_dark else QColor(80, 80, 40)
        )  # light yellow / dark yellow

        fmt = QTextCharFormat()
        fmt.setBackground(highlight_color)

        for line_no in changed_lines:
            block = self.right_editor.document().findBlockByLineNumber(line_no)
            cursor = QTextCursor(block)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.mergeCharFormat(fmt)

        # also optionally show a status
        if changed_lines:
            self.status_label.setText(
                f"Formatted – {len(changed_lines)} lines changed (highlighted in yellow)"
            )
        else:
            self.status_label.setText("Formatted – no visual changes")
