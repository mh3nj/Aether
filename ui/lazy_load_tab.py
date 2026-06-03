import os
from pathlib import Path
from PIL import Image
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QProgressBar, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QApplication, QLineEdit
)
from PySide6.QtCore import Qt
from bs4 import BeautifulSoup

class LazyLoadTab(QWidget):
    def __init__(self):
        super().__init__()
        self.project_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # project folder selection
        folder_row = QHBoxLayout()
        self.folder_label = QLabel("No project folder selected")

        self.select_btn = QPushButton("Select Project Folder (HTML + Images)")
        self.select_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(self.select_btn)
        folder_row.addWidget(self.folder_label)
        folder_row.addStretch()
        layout.addLayout(folder_row)

        # options

        opts_group = QGroupBox("Blur-up Preview Options (WebP, Same Dimensions, Ultra Low Quality)")
        opts_layout = QFormLayout()
        
        self.preview_quality = QSpinBox()
        self.preview_quality.setRange(5, 50)
        self.preview_quality.setValue(15)
        self.preview_quality.setToolTip("Lower = smaller file size, more blurry (5-50)")
        opts_layout.addRow("WebP quality (5-50):", self.preview_quality)
        
        self.downsample = QSpinBox()
        self.downsample.setRange(1, 8)
        self.downsample.setValue(2)
        self.downsample.setToolTip("Reduce color resolution (2-8). Higher = smaller file")
        opts_layout.addRow("Color downsample (1-8):", self.downsample)
        
        self.suffix_edit = QLineEdit("-preview")
        opts_layout.addRow("Preview file suffix:", self.suffix_edit)
        
        self.blur_css_check = QCheckBox("Add CSS blur filter to preview (smoother transition)")
        self.blur_css_check.setChecked(True)
        opts_layout.addRow(self.blur_css_check)
        

        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)

        # buttons  # idk why this works but
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("1. Generate WebP Previews (crappy quality, tiny size)")
        self.scan_btn.clicked.connect(self.generate_previews)
        self.update_btn = QPushButton("2. Update HTML Files")
        self.update_btn.clicked.connect(self.update_html_files)
        self.inject_btn = QPushButton("3. Inject Lazy Load Script")
        self.inject_btn.clicked.connect(self.inject_script)
        btn_row.addWidget(self.scan_btn)
        btn_row.addWidget(self.update_btn)
        btn_row.addWidget(self.inject_btn)
        layout.addLayout(btn_row)

        # progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # log
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(300)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        self.generated_previews = {}  # original_path -> preview_path

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_folder = path
            self.folder_label.setText(path)
            self.log.appendPlainText(f"Project folder: {path}")

    def log_msg(self, msg):
        self.log.appendPlainText(msg)
        QApplication.processEvents()

    def generate_previews(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        # find all image files
        img_extensions = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
        images = []
        for ext in img_extensions:
            images.extend(Path(self.project_folder).rglob(f"*{ext}"))
            images.extend(Path(self.project_folder).rglob(f"*{ext.upper()}"))

        if not images:
            self.log_msg("No images found.")
            return

        self.scan_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setMaximum(len(images))
        self.log.clear()
        self.generated_previews.clear()

        preview_quality = self.preview_quality.value()
        downsample = self.downsample.value()
        suffix = self.suffix_edit.text().strip()
        if not suffix:
            suffix = "-preview"

        for idx, img_path in enumerate(images):
            try:
                # skip if preview already exists  # lol don't ask
                preview_path = img_path.parent / f"{img_path.stem}{suffix}.webp"
                
                img = Image.open(img_path)
                
                # convert to rgb if needed (webp supports rgba, but quality compression works better on rgb)
                if img.mode in ('P', 'LA'):
                    img = img.convert('RGBA')
                elif img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')

                
                # reduce color depth for smaller file size
                if downsample > 1 and img.mode == 'RGBA':
                    # for rgba, preserve alpha but reduce rgb colors
                    r, g, b, a = img.split()
                    rgb_img = Image.merge('RGB', (r, g, b))
                    colors = max(16, 256 // downsample)
                    rgb_img = rgb_img.quantize(colors).convert('RGB')
                    r2, g2, b2 = rgb_img.split()
                    img = Image.merge('RGBA', (r2, g2, b2, a))
                elif downsample > 1:
                    colors = max(16, 256 // downsample)
                    img = img.quantize(colors).convert('RGB')
                
                # save as webp with ultra-low quality, same dimensions
                img.save(preview_path, 'WEBP', quality=preview_quality, method=6, lossless=False, optimize=True)
                
                self.generated_previews[str(img_path)] = str(preview_path)
                original_size = img_path.stat().st_size / 1024
                preview_size_kb = preview_path.stat().st_size / 1024
                self.log_msg(f"✓ {img_path.name}: {original_size:.1f}KB → preview {preview_size_kb:.1f}KB")
                
            except Exception as e:
                self.log_msg(f"✗ Error processing {img_path.name}: {e}")
            self.progress.setValue(idx + 1)
            QApplication.processEvents()

        self.progress.setVisible(False)
        self.scan_btn.setEnabled(True)
        self.status_label.setText(f"Generated {len(self.generated_previews)} WebP preview images.")
        self.log_msg(f"\n \uf00c Done! Generated {len(self.generated_previews)} previews.")
        QMessageBox.information(self, "Done", f"Generated {len(self.generated_previews)} WebP previews.\n\nNow click 'Update HTML Files'.")

    def update_html_files(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return
        if not self.generated_previews:
            QMessageBox.warning(self, "Warning", "No previews found. Run 'Generate WebP Previews' first.")
            return

        html_files = list(Path(self.project_folder).rglob("*.html"))

        if not html_files:
            self.log_msg("No HTML files found.")
            return

        updated = 0
        suffix = self.suffix_edit.text().strip()
        if not suffix:
            suffix = "-preview"
            
        for html_path in html_files:
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
            
            modified = False
            for img in soup.find_all('img'):
                src = img.get('src')
                if not src:
                    continue
                
                # convert windows backslashes to forward slashes for html
                src_normalized = src.replace('\\', '/')
                
                # find original image on disk
                img_file = None
                possible_paths = []
                
                # try different path resolutions
                possible_paths.append(html_path.parent / src_normalized)
                possible_paths.append(Path(self.project_folder) / src_normalized)
                possible_paths.append(Path(self.project_folder) / Path(src_normalized).name)
                
                for candidate in possible_paths:
                    if candidate.exists() and str(candidate) in self.generated_previews:
                        img_file = candidate
                        break
                

                if img_file:
                    preview_path = self.generated_previews[str(img_file)]
                    # get relative path from html to preview (using forward slashes)
                    try:
                        preview_rel = os.path.relpath(preview_path, html_path.parent).replace('\\', '/')
                    except:
                        preview_rel = str(preview_path).replace('\\', '/')
                    
                    # store original src (normalized)
                    original_src = src_normalized
                    
                    # replace src with preview image
                    img['src'] = preview_rel
                    img['data-src'] = original_src
                    
                    # add class
                    existing_classes = img.get('class', [])
                    if isinstance(existing_classes, str):
                        existing_classes = existing_classes.split()
                    if 'lazy-blur' not in existing_classes:
                        existing_classes.append('lazy-blur')
                    img['class'] = ' '.join(existing_classes)
                    
                    modified = True
                    self.log_msg(f"  ✓ Updated: {html_path.name} → {Path(preview_path).name}")
            
            if modified:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                updated += 1

        self.log_msg(f"\n \uf00c Updated {updated} HTML files.")
        if updated > 0:
            self.status_label.setText(f"Updated {updated} HTML files. Click 'Inject Lazy Load Script' to finish.")
            QMessageBox.information(self, "HTML Updated", f"Updated {updated} HTML files.\n\nNow click 'Inject Lazy Load Script'.")

    def inject_script(self):
        if not self.project_folder:
            QMessageBox.warning(self, "Warning", "Select a project folder first.")
            return

        blur_css = """
<style>
img.lazy-blur {
    filter: blur(8px);
    transition: filter 0.3s ease-out, opacity 0.3s ease-out;
}
img.lazy-blur.loaded {

    filter: blur(0);
}
</style>
""" if self.blur_css_check.isChecked() else ""

        js_code = """
<script>

(function() {
    function loadImage(img) {
        const highResSrc = img.getAttribute('data-src');
        if (highResSrc && img.src !== highResSrc) {
            const tempImg = new Image();
            tempImg.onload = function() {
                img.src = highResSrc;
                img.classList.add('loaded');
            };
            tempImg.src = highResSrc;
        }
    }
    
    function initLazyLoad() {
        const lazyImages = document.querySelectorAll('img.lazy-blur');
        
        if ('IntersectionObserver' in window) {

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        loadImage(entry.target);
                        observer.unobserve(entry.target);
                    }
                });

            }, { rootMargin: '100px', threshold: 0.01 });
            lazyImages.forEach(img => observer.observe(img));
        } else {
            lazyImages.forEach(img => loadImage(img));
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLazyLoad);

    } else {
        initLazyLoad();
    }
})();
</script>
"""

        html_files = list(Path(self.project_folder).rglob("*.html"))
        injected = 0
        
        for html_path in html_files:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'lazy-blur' in content and 'IntersectionObserver' in content:
                self.log_msg(f"  Skipped (already injected): {html_path.name}")
                continue
            
            if blur_css and '</head>' in content:
                content = content.replace('</head>', f'{blur_css}\n</head>')
            
            if '</body>' in content:
                content = content.replace('</body>', f'{js_code}\n</body>')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            injected += 1
            self.log_msg(f"  ✓ Injected: {html_path.name}")

        self.log_msg(f"\n \uf00c Injected lazy-load script into {injected} HTML files.")
        QMessageBox.information(self, "Done", f"Lazy loading fully configured for {injected} files!")
