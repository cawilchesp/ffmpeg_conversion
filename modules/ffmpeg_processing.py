import subprocess
from pathlib import Path
from dataclasses import dataclass

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
        raise IOError('Failed to get video info ❌')


def process_video(ffmpeg_path: Path, config: ProcessConfig) -> None:
    # Build output path
    output_path = Path(config.source).with_stem(f"{Path(config.source).stem}_FFMPEG_EDITED.mp4")
    
    # Build FFmpeg command
    cmd = [
        str(ffmpeg_path),
        "-hwaccel", "cuda",
        "-an",
        "-i", config.source,
        "-c:v", "h264_nvenc"
    ]
    
    # Check bitrate
    if config.bitrate:
        cmd.append("-b:v")
        cmd.append(f"{config.bitrate}M")

    # Check resolution
    if config.resolution:
        cmd.append("-vf")
        cmd.append(f"scale={config.resolution}")

    # Check FPS
    if config.fps:
        cmd.append("-r")
        cmd.append(f"{config.fps}")

    cmd.append("-y")
    cmd.append(f"{output_path}")
    
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(result)
    # for line in result.stdout:
    #     print("Progress:", line.strip())
