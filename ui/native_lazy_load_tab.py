"""
Aether Native Lazy Load Tab – Add loading="lazy" to images and videos
Simple, native, zero-JS lazy loading using HTML attributes
"""

import re
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QCheckBox, QSpinBox, QComboBox

)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup



class NativeLazyLoadTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.data_bridge = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # folder selection  # somebody please refactor this
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        self.scan_btn = QPushButton("Scan for Media Files")
        self.scan_btn.clicked.connect(self.scan_files)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.scan_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # options
        opts_group = QGroupBox("Lazy Load Options")
        opts_layout = QVBoxLayout(opts_group)
        
        self.add_images = QCheckBox("Add loading='lazy' to images")
        self.add_images.setChecked(True)
        opts_layout.addWidget(self.add_images)
        
        self.add_videos = QCheckBox("Add loading='lazy' to videos")
        self.add_videos.setChecked(True)
        opts_layout.addWidget(self.add_videos)
        
        self.add_fetch_priority = QCheckBox("Add fetchpriority='low' to offscreen elements")
        self.add_fetch_priority.setChecked(True)
        opts_layout.addWidget(self.add_fetch_priority)
        
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)


        # results tree  # this is cursed but
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["File", "Type", "Element", "Action"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_tree.setAlternatingRowColors(True)
        layout.addWidget(self.results_tree)

        # progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # inject button
        self.inject_btn = QPushButton("Inject Native Lazy Loading Attributes")
        self.inject_btn.clicked.connect(self.inject_attributes)
        self.inject_btn.setEnabled(False)
        layout.addWidget(self.inject_btn)

        # info label
        info_label = QLabel(
            "Note: loading='lazy' is supported in all modern browsers.\n"
            "Images/videos will only load when they scroll into view.\n"
            "This saves bandwidth and speeds up initial page load."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #8095ab; padding: 5px;")

        layout.addWidget(info_label)

        self.summary_label = QLabel("Ready - Select a folder and click Scan")
        layout.addWidget(self.summary_label)

        self.elements_to_update = []

    def set_data_bridge(self, bridge):
        self.data_bridge = bridge

    def select_folder(self):

        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)

    def scan_files(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a folder first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))
        if not html_files:
            self.summary_label.setText("No HTML files found.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(html_files))
        self.results_tree.clear()
        self.elements_to_update = []

        for idx, html_path in enumerate(html_files):
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                rel_path = str(html_path.relative_to(self.project_folder))

                # scan for images
                if self.add_images.isChecked():
                    for img in soup.find_all('img'):
                        if not img.get('loading'):
                            self.elements_to_update.append({

                                'file': str(html_path),
                                'rel_path': rel_path,
                                'type': 'Image',
                                'element': img,
                                'src': img.get('src', 'unknown')[:50],
                                'action': 'Add loading="lazy"'
                            })
                            item = QTreeWidgetItem([rel_path, "Image", img.get('src', 'unknown')[:50], "Will add loading='lazy'"])
                            self.results_tree.addTopLevelItem(item)

                # scan for videos
                if self.add_videos.isChecked():
                    for video in soup.find_all('video'):
                        if not video.get('loading'):
                            self.elements_to_update.append({
                                'file': str(html_path),
                                'rel_path': rel_path,
                                'type': 'Video',
                                'element': video,
                                'src': video.get('src', 'unknown')[:50],
                                'action': 'Add loading="lazy"'
                            })
                            item = QTreeWidgetItem([rel_path, "Video", video.get('src', 'unknown')[:50], "Will add loading='lazy'"])
                            self.results_tree.addTopLevelItem(item)


            except Exception as e:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)

        if self.elements_to_update:
            self.inject_btn.setEnabled(True)
            self.summary_label.setText(f"Found {len(self.elements_to_update)} elements that can benefit from native lazy loading.")
        else:
            self.inject_btn.setEnabled(False)
            self.summary_label.setText("No elements found. All images/videos already have lazy loading!")

    def inject_attributes(self):
        if not self.elements_to_update:
            QMessageBox.warning(self, "Warning", "No elements to update. Run scan first.")
            return

        reply = QMessageBox.question(self, "Confirm Injection",
                                     f"Inject native lazy loading attributes to {len(self.elements_to_update)} elements?\n\n"
                                     f"This will add loading='lazy' to images and videos.\n\n"
                                     f"Proceed?",

                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        self.inject_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.elements_to_update))

        updated = 0
        files_modified = set()

        for idx, element_data in enumerate(self.elements_to_update):
            try:
                with open(element_data['file'], 'r', encoding='utf-8') as f:

                    soup = BeautifulSoup(f, 'html.parser')


                # find and update the specific element  # this is why we cant have nice things
                for tag in soup.find_all(element_data['element'].name):
                    if tag.get('src') == element_data['element'].get('src'):
                        tag['loading'] = 'lazy'
                        if self.add_fetch_priority.isChecked():
                            tag['fetchpriority'] = 'low'
                        updated += 1
                        break

                with open(element_data['file'], 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                files_modified.add(element_data['rel_path'])


                # update tree item
                item = self.results_tree.topLevelItem(idx)
                if item:
                    item.setText(3, "Added loading='lazy'")

            except Exception as e:
                pass

            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.inject_btn.setEnabled(True)

        # report to dashboard
        if self.data_bridge and updated > 0:
            self.data_bridge.report_fix("native lazy load", updated)

        self.summary_label.setText(f"Injected lazy loading into {updated} elements across {len(files_modified)} files.")
        QMessageBox.information(self, "Injection Complete", 
                                f"Added loading='lazy' to {updated} images/videos.\n\n"
                                f"Browsers will now defer loading off-screen media.")

    def update_theme(self, is_dark):
        if is_dark:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #2b2d31;

                    color: #e8e8e8;
                    alternate-background-color: #3e4045;
                }
                QHeaderView::section {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
            """)
        else:
            self.results_tree.setStyleSheet("""
                QTreeWidget {
                    background-color: #ffffff;
                    color: #2c3e50;
                    alternate-background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #f1f3f5;
                    color: #2c3e50;
                    border: 1px solid #d0d7de;
                }
            """)