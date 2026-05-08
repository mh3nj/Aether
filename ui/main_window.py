from PySide6.QtWidgets import QMainWindow, QTabWidget
from ui.formatter_tab import FormatterTab
from ui.seo_tab import SEOTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Dev Tools – Formatter + SEO")
        self.setGeometry(100, 100, 1200, 800)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        tabs.addTab(FormatterTab(), "Code Formatter")
        tabs.addTab(SEOTab(), "SEO Optimizer")

        self.statusBar().showMessage("Ready")
