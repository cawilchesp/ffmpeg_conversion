import re
import subprocess
from pathlib import Path
from dataclasses import dataclass
from rich.live import Live
from rich import print, box
from rich.table import Table, Column

# Local modules
from modules.process_config import ProcessConfig


@dataclass
class VideoInfo:
    """ Class to hold video information.
    Attributes:
        source (str): The video source path or identifier.
        width (str): The width of the video in pixels.
        height (str): The height of the video in pixels.
        fps (str): The frames per second of the video.
        total_frames (str): The total number of frames in the video.
    """
    source_name: str
    width: str
    height: str
    fps: str
    total_frames: str

        
def load_video_info(ffmpeg_path: Path, source: str) -> VideoInfo:
    """ Load video information using ffprobe.
    Args:
        ffmpeg_path (Path): Path to the ffmpeg executable.
        source (str): The video source path or identifier.
    Returns:
        VideoInfo: An instance of VideoInfo containing video details.
    Raises:
        IOError: If the video information cannot be retrieved.
    """
    try:
        result = subprocess.run([
            str(ffmpeg_path.parent / "ffprobe"),
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration,codec_name",
            "-of", "default=noprint_wrappers=1",
            source
        ], capture_output=True, text=True, check=True)
        
        info = {}
        for line in result.stdout.split('\n'):
            if '=' in line:
                key, value = line.split('=')
                info[key.strip()] = value.strip()
        
        return VideoInfo(
            source_name=Path(source).stem,
            width=info.get('width', 'N/A'),
            height=info.get('height', 'N/A'),
            fps=eval(info.get('r_frame_rate', '0/1')),
            total_frames=info.get('nb_frames', 'N/A')
        )
    except Exception as e:
        raise IOError(f'❌ Failed to get video info: {str(e)} ')


def process_video(ffmpeg_path: Path, config: ProcessConfig) -> subprocess.Popen:
    # Build output path
    output_path = Path(config.source).with_stem(f"{Path(config.source).stem}_FFMPEG_EDITED.mp4")
    
    # Build FFmpeg command
    cmd = [
        str(ffmpeg_path),
        "-hwaccel", "cuda",
        "-y",
        "-an",
        "-i", config.source,
        "-c:v", "h264_nvenc"
    ]

    # Video encoding options
    options = {
        "bitrate": ["-b:v", f"{config.bitrate}M"],
        "resolution": ["-vf", f"scale={config.resolution}"],
        "fps": ["-r", f"{config.fps}"]
    }

    for key, args in options.items():
        if getattr(config, key):
            cmd.extend(args)

    cmd.append(f"{output_path}")
    
    # Launch process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    return process


def monitor_process(process: subprocess.Popen) -> tuple[str, str, str, str]:
    """ Monitor the FFmpeg process and display progress."""
    progress_pattern = re.compile(r"frame=\s*(\d+).*?fps=\s*([\d\.]+).*?time=\s*(\d+:\d+:\d+\.\d+).*?speed=\s*([\d\.]+)x")

    with Live(monitor_table("0","0.0","-","0.0"), refresh_per_second=4) as live:
        while True:
            line = process.stderr.readline()
            if not line:
                break
            line = line.strip()

            # Show errors
            if "Error" in line or "Invalid" in line or "failed" in line.lower():
                print(f"[bold red]Error:[/bold red] {line}")

            # Match progress line
            match = progress_pattern.search(line)
            if match:
                frame, fps, timestamp, speed = match.groups()
                live.update(monitor_table(frame, fps, timestamp, speed))


def monitor_table(frame: str, fps: str, timestamp: str, speed: str) -> Table:
    """Display video source information in a formatted table.
    Args:
        video_info (VideoInfo): Information about the video source.
    """
    table = Table(
        Column("Frame", justify="left", style="white", no_wrap=True),
        Column("Frame Rate", justify="left", style="white", no_wrap=True),
        Column("Video Time", justify="left", style="white", no_wrap=True),
        Column("Speed", justify="left", style="white", no_wrap=True),
        title="Processing",
        box=box.HORIZONTALS )

    table.add_row(
        f"{frame}",
        f"{fps} FPS",
        f"{timestamp}",
        f"{speed}x")
        
    return table

def crop_detect(ffmpeg_path: Path, config: ProcessConfig) -> subprocess.Popen:
    cmd = [
        str(ffmpeg_path),
        "-i", config.source,
        "-vf", "cropdetect",
        "-an", "-t", "1", "-f", "null","-"
    ]

    # Launch process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    return process

def crop_result(process: subprocess.Popen) -> tuple[str, str, str, str]:
    progress_pattern = re.compile(r"crop=\s*(\d+:\d+:\d+\:\d+)")

    while True:
        line = process.stderr.readline()
        if not line:
            break
        line = line.strip()

        # Show errors
        if "Error" in line or "Invalid" in line or "failed" in line.lower():
            print(f"[bold red]Error:[/bold red] {line}")

        # Match progress line
        match = progress_pattern.search(line)
        if match:
            width, height, x, y = match.groups()[0].split(':')

            return (width, height, x, y)
        
def crop_video(ffmpeg_path: Path, config: ProcessConfig) -> subprocess.Popen:
    # Build output path
    output_path = Path(config.source).with_stem(f"{Path(config.source).stem}_FFMPEG_EDITED.mp4")
    
    cmd = [
        str(ffmpeg_path),
        "-i", config.source,
        "-vf", "cropdetect",
        "-an", "-t", "1", "-f", "null","-"
    ]
    
    return None