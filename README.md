# ffmpeg_conversion

**ffmpeg_conversion** is a Python-based tool for video conversion using FFMPEG. It is designed to be modular and easy to use.

## Features

- Video conversion for resolution, bitrate, and frame rate.
- Video cropping with automatic crop area detection.
- Modular architecture.

## Project Structure

- main.py: Entry point for running the tracker
- ffmpeg: Folder containing FFMPEG. Its path can be customized with parameter `--ffmpeg`.
- modules/
    - process_config.py: Configuration processing.
    - ffmpeg_processing.py: Video conversion and cropping processing.
- tools/
    - messages.py: Messaging helpers

## Usage

- Place your input videos or images in the appropriate directory.
- Run `main.py` to start detection and tracking.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Carlos Andrés Wilches Pérez