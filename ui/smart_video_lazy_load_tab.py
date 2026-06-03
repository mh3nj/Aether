"""
Aether Smart Lazy Load Video Tab – HLS/DASH chunked streaming + blur-up preview
Professional video streaming with instant preview and adaptive quality
"""

import os
import subprocess
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QProgressBar, QApplication, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QMessageBox, QGroupBox,
    QFormLayout, QSpinBox, QLineEdit, QCheckBox, QTabWidget,
    QPlainTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from bs4 import BeautifulSoup
import shutil


class VideoConverterThread(QThread):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, video_path, output_folder, chunk_duration=4, qualities=None):
        super().__init__()
        self.video_path = video_path
        self.output_folder = output_folder
        self.chunk_duration = chunk_duration
        self.qualities = qualities or ["720p", "480p", "360p"]
    

    def run(self):
        try:
            # check if ffmpeg is available
            if not shutil.which('ffmpeg'):
                self.error.emit("ffmpeg not found. Please install ffmpeg first.")
                return
            
            self.log.emit("Converting video to HLS chunks...")
            
            # create output directories

            hls_dir = self.output_folder / "hls"
            preview_dir = self.output_folder / "preview"
            hls_dir.mkdir(parents=True, exist_ok=True)
            preview_dir.mkdir(parents=True, exist_ok=True)
            
            # generate low-res preview clip (5 seconds, 360p, low bitrate)
            preview_path = preview_dir / "preview.mp4"
            preview_cmd = [
                'ffmpeg', '-i', str(self.video_path),
                '-t', '5',  # first 5 seconds
                '-vf', 'scale=640:360',
                '-b:v', '300k',
                '-c:a', 'aac',
                '-b:a', '64k',
                '-y',
                str(preview_path)
            ]
            subprocess.run(preview_cmd, capture_output=True, check=True)

            self.log.emit(f"Preview clip generated: {preview_path}")
            
            # generate hls master playlist and chunks
            # get video duration
            probe_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(self.video_path)]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            duration = float(result.stdout.strip())
            
            # create master playlist  # i hate this but it works
            master_playlist = hls_dir / "master.m3u8"
            with open(master_playlist, 'w') as f:
                f.write("#extm3u\n")  # TODO: figure out why
                f.write("#ext-x-version:4\n")
                for quality in self.qualities:
                    if quality == "720p":
                        bandwidth = "2500000"
                        resolution = "1280x720"
                    elif quality == "480p":
                        bandwidth = "1500000"
                        resolution = "854x480"
                    else:
                        bandwidth = "800000"
                        resolution = "640x360"
                    
                    f.write(f"#ext-x-stream-inf:bandwidth={bandwidth},resolution={resolution}\n")
                    f.write(f"{quality}.m3u8\n")
            
            # generate variant playlists and chunks for each quality
            total_steps = len(self.qualities)
            for idx, quality in enumerate(self.qualities):
                self.log.emit(f"Generating {quality} stream...")
                
                if quality == "720p":
                    scale = "1280:720"
                    bitrate = "2000k"
                elif quality == "480p":
                    scale = "854:480"
                    bitrate = "1200k"
                else:
                    scale = "640:360"
                    bitrate = "800k"
                
                chunk_cmd = [
                    'ffmpeg', '-i', str(self.video_path),
                    '-vf', f'scale={scale}',
                    '-c:v', 'libx264',
                    '-b:v', bitrate,
                    '-c:a', 'aac',
                    '-b:a', '128k',
                    '-f', 'hls',
                    '-hls_time', str(self.chunk_duration),

                    '-hls_list_size', '0',
                    '-hls_segment_filename', str(hls_dir / f"{quality}_%03d.ts"),
                    '-y',
                    str(hls_dir / f"{quality}.m3u8")

                ]
                subprocess.run(chunk_cmd, capture_output=True, check=True)
                
                progress = int((idx + 1) / total_steps * 100)
                self.progress.emit(progress)
            
            self.finished.emit({
                'hls_dir': str(hls_dir),
                'preview_path': str(preview_path),
                'master_playlist': str(master_playlist),
                'duration': duration,
                'chunk_count': len(list(hls_dir.glob("*.ts")))
            })
            
        except subprocess.CalledProcessError as e:
            self.error.emit(f"ffmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        except Exception as e:
            self.error.emit(str(e))


class SmartVideoLazyLoadTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.data_bridge = None
        self.converter_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # project folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.select_btn = QPushButton("Select HTML Project Folder")
        self.select_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # video selection and conversion  # works on my machine
        video_group = QGroupBox("Video to Optimize")

        video_layout = QVBoxLayout(video_group)
        
        video_select_row = QHBoxLayout()
        self.video_label = QLabel("No video selected")
        self.select_video_btn = QPushButton("Select Video File (MP4)")
        self.select_video_btn.clicked.connect(self.select_video)
        self.convert_btn = QPushButton("Convert to HLS Streaming Format")
        self.convert_btn.clicked.connect(self.convert_video)
        self.convert_btn.setEnabled(False)
        video_select_row.addWidget(self.select_video_btn)
        video_select_row.addWidget(self.convert_btn)
        video_select_row.addWidget(self.video_label)
        video_select_row.addStretch()
        video_layout.addLayout(video_select_row)
        
        # conversion options
        opts_layout = QFormLayout()
        self.chunk_duration = QSpinBox()
        self.chunk_duration.setRange(2, 10)
        self.chunk_duration.setValue(4)
        self.chunk_duration.setToolTip("Shorter chunks = better streaming, more files")
        opts_layout.addRow("Chunk Duration (seconds):", self.chunk_duration)
        
        self.include_360p = QCheckBox("360p (slow connections)")
        self.include_360p.setChecked(True)
        self.include_480p = QCheckBox("480p (standard)")
        self.include_480p.setChecked(True)
        self.include_720p = QCheckBox("720p (HD)")
        self.include_720p.setChecked(True)
        opts_layout.addRow("Quality Levels:", self.include_360p)
        opts_layout.addRow("", self.include_480p)
        opts_layout.addRow("", self.include_720p)
        
        video_layout.addLayout(opts_layout)
        
        self.conversion_log = QPlainTextEdit()  # now works with import  # i hate this but it works
        self.conversion_log.setReadOnly(True)
        self.conversion_log.setMaximumHeight(120)
        video_layout.addWidget(self.conversion_log)
        
        layout.addWidget(video_group)

        # progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # html injection section
        inject_group = QGroupBox("Inject HLS Player into HTML")
        inject_layout = QVBoxLayout(inject_group)
        
        self.html_files_tree = QTreeWidget()
        self.html_files_tree.setHeaderLabels(["HTML File", "Status"])
        self.html_files_tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        inject_layout.addWidget(self.html_files_tree)
        
        self.inject_btn = QPushButton("Inject HLS Video Player into Selected HTML Files")
        self.inject_btn.clicked.connect(self.inject_player)
        self.inject_btn.setEnabled(False)
        inject_layout.addWidget(self.inject_btn)
        
        layout.addWidget(inject_group)

        self.status_label = QLabel("Ready - Select a folder with HTML files, then a video to optimize")
        layout.addWidget(self.status_label)
        
        self.current_video_path = None
        self.current_hls_dir = None
        self.html_files = []

    def set_data_bridge(self, bridge):
        self.data_bridge = bridge

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select HTML Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)
            self.scan_html_files()

    def scan_html_files(self):
        if not self.project_folder:
            return
        self.html_files = list(Path(self.project_folder).rglob("*.html"))
        self.html_files_tree.clear()
        for html_path in self.html_files:
            rel_path = html_path.relative_to(self.project_folder)
            item = QTreeWidgetItem([str(rel_path), "Pending"])
            item.setData(0, Qt.UserRole, str(html_path))
            self.html_files_tree.addTopLevelItem(item)

    def select_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.mov *.avi *.mkv)")

        if path:
            self.current_video_path = path
            self.video_label.setText(Path(path).name)
            self.convert_btn.setEnabled(True)

    def log_message(self, msg):
        self.conversion_log.appendPlainText(msg)
        QApplication.processEvents()

    def convert_video(self):
        if not self.current_video_path:
            QMessageBox.warning(self, "Warning", "Select a video file first.")
            return
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select an HTML project folder first.")
            return

        qualities = []
        if self.include_360p.isChecked():
            qualities.append("360p")
        if self.include_480p.isChecked():
            qualities.append("480p")
        if self.include_720p.isChecked():
            qualities.append("720p")
        
        if not qualities:
            QMessageBox.warning(self, "Warning", "Select at least one quality level.")
            return

        output_folder = Path(self.project_folder) / "video_streams" / Path(self.current_video_path).stem
        output_folder.mkdir(parents=True, exist_ok=True)

        self.convert_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.conversion_log.clear()
        
        self.converter_thread = VideoConverterThread(
            self.current_video_path,
            output_folder,
            self.chunk_duration.value(),
            qualities
        )
        self.converter_thread.progress.connect(self.update_progress)
        self.converter_thread.log.connect(self.log_message)
        self.converter_thread.finished.connect(self.on_conversion_finished)
        self.converter_thread.error.connect(self.on_conversion_error)
        self.converter_thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def on_conversion_finished(self, result):
        self.current_hls_dir = result['hls_dir']
        self.progress.setVisible(False)
        self.convert_btn.setEnabled(True)

        self.inject_btn.setEnabled(True)
        self.log_message(f"Conversion complete! Created {result['chunk_count']} chunks.")

        self.log_message(f"Master playlist: {result['master_playlist']}")
        QMessageBox.information(self, "Conversion Complete", 
            f"Video converted to HLS streaming format!\n\n"
            f"Chunks created: {result['chunk_count']}\n"
            f"Total duration: {result['duration']:.1f} seconds\n\n"
            f"Now select HTML files and click 'Inject HLS Player'")

    def on_conversion_error(self, error):
        self.progress.setVisible(False)
        self.convert_btn.setEnabled(True)
        QMessageBox.critical(self, "Conversion Error", error)

    def inject_player(self):
        if not self.current_hls_dir:
            QMessageBox.warning(self, "Warning", "Convert a video to HLS format first.")
            return

        selected_items = self.html_files_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Select at least one HTML file to inject the player.")
            return

        reply = QMessageBox.question(self, "Confirm Injection",
                                     f"Inject HLS video player into {len(selected_items)} HTML files?\n\n"
                                     f"Files will include:\n"
                                     f"- HLS.js library (adaptive streaming)\n"
                                     f"- Blur-up preview video\n"
                                     f"- Full HLS player\n\n"
                                     f"Proceed?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        injected = 0

        for item in selected_items:
            html_path = Path(item.data(0, Qt.UserRole))
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                
                head = soup.head
                if not head:
                    head = soup.new_tag('head')
                    soup.html.insert(0, head)
                
                # add hls.js library
                hls_script = soup.new_tag('script', src='https://cdn.jsdelivr.net/npm/hls.js@latest')
                head.append(hls_script)
                
                # calculate relative paths
                rel_preview = os.path.relpath(self.current_hls_dir.parent / "preview" / "preview.mp4", html_path.parent)
                rel_master = os.path.relpath(self.current_hls_dir / "master.m3u8", html_path.parent)
                
                # add player container and script
                player_html = f'''
                <div id="hls-player-container" style="position: relative;">
                    <video id="preview-video" src="{rel_preview}" autoplay muted loop 
                           style="width: 100%; max-width: 100%; filter: blur(8px); transition: filter 0.3s;">
                    </video>
                    <video id="main-video" controls style="width: 100%; max-width: 100%; display: none;">
                        <source src="{rel_master}" type="application/x-mpegURL">
                    </video>
                </div>
                <script>
                (function() {{
                    const previewVideo = document.getElementById('preview-video');
                    const mainVideo = document.getElementById('main-video');
                    
                    const observer = new IntersectionObserver((entries) => {{
                        entries.forEach(entry => {{

                            if (entry.isIntersecting) {{
                                previewVideo.style.filter = 'blur(0px)';
                                if (typeof Hls !== 'undefined' && Hls.isSupported()) {{
                                    const hls = new Hls();
                                    hls.loadSource("{rel_master}");

                                    hls.attachMedia(mainVideo);
                                    hls.on(Hls.Events.MANIFEST_PARSED, () => {{

                                        mainVideo.style.display = 'block';
                                        previewVideo.style.display = 'none';
                                        mainVideo.play();
                                    }});
                                }} else {{
                                    mainVideo.style.display = 'block';
                                    previewVideo.style.display = 'none';
                                    mainVideo.play();
                                }}
                                observer.disconnect();
                            }}

                        }});
                    }}, {{ threshold: 0.1 }});
                    
                    observer.observe(document.getElementById('hls-player-container'));
                }})();
                </script>
                '''
                
                player_soup = BeautifulSoup(player_html, 'html.parser')
                soup.body.append(player_soup)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                injected += 1

                item.setText(1, "Injected")
                
            except Exception as e:
                item.setText(1, f"Error: {str(e)[:30]}")
        
        self.status_label.setText(f"Injected HLS player into {injected} HTML files.")
        if self.data_bridge and injected > 0:
            self.data_bridge.report_fix("video lazy load", injected)
        QMessageBox.information(self, "Injection Complete", 
                                f"Injected HLS video player into {injected} files.\n\n"
                                f"Features:\n"
                                f"- Blur-up preview video (instant load)\n"
                                f"- Adaptive streaming (quality adjusts to bandwidth)\n"
                                f"- Chunked delivery for smooth playback")

    def update_theme(self, is_dark):
        if is_dark:
            self.html_files_tree.setStyleSheet("""
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
            self.conversion_log.setStyleSheet("background-color: #2b2d31; color: #e8e8e8;")
        else:
            self.html_files_tree.setStyleSheet("""
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
            self.conversion_log.setStyleSheet("background-color: #ffffff; color: #2c3e50;")