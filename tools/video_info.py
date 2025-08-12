from __future__ import annotations

import cv2
from pathlib import Path

class VideoInfo:
    def __init__(
        self,
        source: str,
        width: int = 0,
        height: int = 0,
        fps: float = 0,
        total_frames: int = None
    ) -> None:
        self.source = source
        self.width = width
        self.height = height
        self.fps = fps
        self.total_frames = total_frames

        self.get_source_info()

    @property
    def resolution_wh(self) -> tuple[int, int]:
        return self.width, self.height


    def get_source_info(self) -> VideoInfo:
        if self.source.isnumeric():
            self.source_name = "Webcam"
            self.source_type = 'stream'
            video_source = int(self.source)
        elif self.source.lower().startswith('rtsp://'):
            self.source_name = "RSTP Stream"
            self.source_type = 'stream'
            video_source = self.source
        else:
            self.source_name = Path(self.source).name
            self.source_type = 'file'
            video_source = self.source

        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened(): raise Exception('Source video not available ❌')

        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if self.source_type == 'file' else None
        
        cap.release()
