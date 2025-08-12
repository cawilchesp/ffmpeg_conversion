import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QLineEdit, QComboBox,
                              QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class VideoProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = Path("bin/ffmpeg.exe")
        self.setup_ui()
        self.setStyleSheet("""
            QWidget { background: #2E2E2E; color: #FFFFFF; }
            QPushButton { background: #4A90D9; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background: #357ABD; }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background: #404040; border: 1px solid #505050; padding: 4px;
            }
        """)

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # File Selection
        self.file_layout = QHBoxLayout()
        self.file_btn = QPushButton("Select Video File")
        self.file_btn.clicked.connect(self.select_file)
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_layout.addWidget(self.file_btn)
        self.file_layout.addWidget(self.file_path)
        
        # Video Info Display
        self.info_label = QLabel("Video Info: None selected")
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(320, 180)

        # Processing Parameters
        self.bitrate_layout = QHBoxLayout()
        self.bitrate_input = QSpinBox()
        self.bitrate_input.setRange(1, 100000)
        self.bitrate_input.setValue(3)
        self.bitrate_unit = QComboBox()
        self.bitrate_unit.addItems(["Kbps", "Mbps", "Gbps"])
        self.bitrate_unit.setCurrentIndex(1)
        self.bitrate_layout.addWidget(QLabel("Bitrate:"))
        self.bitrate_layout.addWidget(self.bitrate_input)
        self.bitrate_layout.addWidget(self.bitrate_unit)

        self.resolution_layout = QHBoxLayout()
        self.width_input = QSpinBox()
        self.width_input.setRange(1, 7680)
        self.width_input.setValue(1280)
        self.height_input = QSpinBox()
        self.height_input.setRange(1, 4320)
        self.height_input.setValue(720)
        self.resolution_layout.addWidget(QLabel("Resolution:"))
        self.resolution_layout.addWidget(self.width_input)
        self.resolution_layout.addWidget(QLabel("x"))
        self.resolution_layout.addWidget(self.height_input)

        self.fps_layout = QHBoxLayout()
        self.fps_input = QDoubleSpinBox()
        self.fps_input.setRange(1.0, 1000.0)
        self.fps_input.setValue(30.0)
        self.fps_layout.addWidget(QLabel("FPS:"))
        self.fps_layout.addWidget(self.fps_input)

        # Process Button
        self.process_btn = QPushButton("Process Video")
        self.process_btn.clicked.connect(self.process_video)

        # Assemble UI
        main_layout.addLayout(self.file_layout)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.preview_label)
        main_layout.addLayout(self.bitrate_layout)
        main_layout.addLayout(self.resolution_layout)
        main_layout.addLayout(self.fps_layout)
        main_layout.addWidget(self.process_btn)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Video Processor Pro")
        self.setMinimumSize(600, 500)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.mov *.avi *.3gp *.mkv)")
        if path:
            self.file_path.setText(path)
            self.load_video_info(path)
            self.extract_middle_frame(path)

    def load_video_info(self, path):
        try:
            result = subprocess.run([
                str(self.ffmpeg_path.parent / "ffprobe"),
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration,codec_name",
                "-of", "default=noprint_wrappers=1",
                path
            ], capture_output=True, text=True, check=True)
            
            info = {}
            for line in result.stdout.split('\n'):
                if '=' in line:
                    key, value = line.split('=')
                    info[key.strip()] = value.strip()
            
            self.info_label.setText(
                f"Resolution: {info.get('width', 'N/A')}x{info.get('height', 'N/A')}\n"
                f"FPS: {eval(info.get('r_frame_rate', '0/1')):.2f}\n"
                f"Duration: {float(info.get('duration', 0)):.2f}s\n"
                f"Codec: {info.get('codec_name', 'N/A')}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get video info: {str(e)}")

    def extract_middle_frame(self, path):
        try:
            duration = float(subprocess.check_output([
                str(self.ffmpeg_path.parent / "ffprobe"),
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path
            ]).decode().strip())
            
            mid_time = duration / 2
            output_path = "middle_frame.jpg"
            
            subprocess.run([
                str(self.ffmpeg_path),
                "-ss", str(mid_time),
                "-i", path,
                "-frames:v", "1",
                "-y", output_path
            ], check=True)
            
            self.preview_label.setPixmap(QPixmap(output_path).scaled(
                320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Frame extraction failed: {str(e)}")

    def process_video(self):
        if not self.ffmpeg_path.exists():
            QMessageBox.critical(self, "Error", "FFmpeg not found in specified path")
            return
            
        input_path = self.file_path.text()
        if not input_path:
            QMessageBox.warning(self, "Warning", "Please select a video file first")
            return

        # Build output path
        output_path = Path(input_path).with_stem(f"{Path(input_path).stem}_processed")
        
        # Build FFmpeg command
        bitrate = f"{self.bitrate_input.value()}{self.bitrate_unit.currentText()[0]}"
        cmd = [
            str(self.ffmpeg_path),
            "-hwaccel", "cuda",
            "-i", input_path,
            "-vf", f"scale={self.width_input.value()}:{self.height_input.value()}",
            "-c:v", "h264_nvenc",
            "-b:v", bitrate,
            "-r", str(self.fps_input.value()),
            "-c:a", "copy",
            "-y", str(output_path)+".mp4"
        ]

        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Success", 
                f"Video processed successfully!\nSaved to: {output_path}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Processing failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoProcessor()
    window.show()
    sys.exit(app.exec())
