import os
import argparse
import itertools
import subprocess
from pathlib import Path

# Local modules
from modules.process_config import ProcessConfig, create_config

# Local tools
import tools.messages as messages


# For debugging
from icecream import ic


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the video conversion tool using FFMPEG.
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Video conversion tool using FFMPEG")
    parser.add_argument('--source', type=str, required=True, help='video source')
    parser.add_argument('--ffmpeg', type=str, default='bin/ffmpeg.exe', help='ffmpeg path')
    parser.add_argument('--bitrate', type=str, nargs='?', const='3', default=False, help='bitrate in Mbps')
    parser.add_argument('--resolution', type=str, nargs='?', const='1920:1080', default=False, help='video resolution')
    parser.add_argument('--fps', type=str, nargs='?', const='30', default=False, help='video fps')
    parser.add_argument('--crop-detect', action='store_true', help='detect crop area')

    return parser.parse_args()


def main(config: ProcessConfig) -> None:
    # Initialize process counter
    step_count = itertools.count(1)

    ffmpeg_path = Path("bin/ffmpeg.exe")

    output_path = f"{Path(source).parent}/{Path(source).stem}_FFMPEG_EDITED.mp4"


    if crop_detect:
        ffmpeg_command = [
            ffmpeg_path,
            "-i", source,
            "-vf", "cropdetect",
            "-an", "-t", "10", "-f", "null","-"
        ]
        # Ejecutar el comando
        messages.step_message(next(step_count), 'Detección de Área de Cortado Iniciado ✅')
    else:

    # ffmpeg -hwaccel cuda -i "D:\INTEIA\Proyectos\Aforos_Medellin\2_Popular\videos\2_3_PM_Crr39_89a_20241106_162201.mp4" -vf "crop=960:720:160:0" -c:v h264_nvenc -c:a copy "D:\INTEIA\Proyectos\Aforos_Medellin\2_Popular\videos\2_3_PM_Crr39_89a_20241106_162201__cropped.mp4"


    # ffmpeg -hwaccel cuda -i "D:\INTEIA\Proyectos\Aforos_Medellin\2_Popular\videos\2_14_PM_Crr45a_Cl93_20241102_154808.mp4" -vf "crop=1440:1080:240:0" -c:v h264_nvenc -c:a copy -b:v 3M "D:\INTEIA\Proyectos\Aforos_Medellin\2_Popular\videos\2_14_PM_Crr45a_Cl93_20241102_154808__cropped.mp4"

        ffmpeg_command = [
            ffmpeg_path, "-y",
            "-vsync", "cfr",
            "-hwaccel", "cuda", "-i", source,
            "-an",
            "-c:v", "h264_nvenc"
        ]
        # ic(ffmpeg_command)
        # quit()

        if bitrate:
            ffmpeg_command.append("-b:v")
            ffmpeg_command.append(f"{bitrate}M")

        if resolution:
            ffmpeg_command.append("-vf")
            ffmpeg_command.append(f"scale_cuda={resolution}")

        if fps:
            ffmpeg_command.append("-r")
            ffmpeg_command.append(f"{fps}")

        ffmpeg_command.append(output_path)
    
        # Ejecutar el comando
        messages.step_message(next(step_count), 'Proceso de Conversión Iniciado ✅')
    


    
    try:
        subprocess.run(ffmpeg_command, check=True)
        messages.step_message(next(step_count), f"Procesado exitosamente: {Path(source).stem} ✅")
    except subprocess.CalledProcessError as e:
        messages.step_message(next(step_count), f"Error al procesar {Path(source).stem}: {e}")

    messages.step_message(next(step_count), 'Proceso de Conversión Finalizado ✅')
    

if __name__ == "__main__":
    options = parse_arguments()
    config = create_config(options)

    main(config)
