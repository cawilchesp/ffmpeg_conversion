from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ProcessConfig:
    """Configuration settings for object detection/tracking
    Attributes:
        source (str): Video source (file path or camera index)
        ffmpeg_path (str): Path to the ffmpeg executable
        bitrate (str): Bitrate in Mbps
        resolution (str): Video resolution
        fps (str): Video frames per second
        crop_detect (bool): Enable crop area detection
    """
    source: str
    ffmpeg_path: str
    bitrate: str
    resolution: str
    fps: str
    crop_detect: bool

def create_config(args) -> ProcessConfig:
    """Create configuration from command line arguments
    Args:
        root_path (Path): Root path of the project
        args (argparse.Namespace): Parsed command line arguments
    """
    return ProcessConfig(
        source=args.source,
        ffmpeg_path=args.ffmpeg,
        bitrate=args.bitrate,
        resolution=args.resolution,
        fps=args.fps,
        crop_detect=args.crop_detect
    )