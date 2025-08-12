import os
import argparse
import itertools
import subprocess
from pathlib import Path

import tools.messages as messages


# For debugging
from icecream import ic

def main(
    source: str,
    ffmpeg_path: str,
    bitrate: str,
    resolution: str,
    fps: str,
    crop_detect: bool
) -> None:
    # Inicializar contador de etapas del proceso de detección y seguimientos
    step_count = itertools.count(1)

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
    # Inicializar argumentos de entrada
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=str, required=True, help='video source')
    parser.add_argument('--ffmpeg', type=str, default='bin/ffmpeg.exe', help='ffmpeg path')
    parser.add_argument('--bitrate', type=str, nargs='?', const='3', default=False, help='bitrate in Mbps')
    parser.add_argument('--resolution', type=str, nargs='?', const='1920:1080', default=False, help='video resolution')
    parser.add_argument('--fps', type=str, nargs='?', const='30', default=False, help='video fps')
    parser.add_argument('--crop-detect', action='store_true', help='detect crop area')
    option = parser.parse_args()

    # Carpeta raíz del proyecto
    root_path = Path(__file__).resolve().parent

    main(
        source=option.source,
        ffmpeg_path=option.ffmpeg,
        bitrate=option.bitrate,
        resolution=option.resolution,
        fps=option.fps,
        crop_detect=option.crop_detect
    )