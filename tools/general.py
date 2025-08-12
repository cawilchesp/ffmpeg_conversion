import json
from typing import Generator, List

import cv2
import numpy as np
import torch
import time
from collections import deque


def find_in_list(array: np.ndarray, search_list: List[int]) -> np.ndarray:
    """Determines if elements of a numpy array are present in a list.

    Args:
        array (np.ndarray): The numpy array of integers to check.
        search_list (List[int]): The list of integers to search within.

    Returns:
        np.ndarray: A numpy array of booleans, where each boolean indicates whether
        the corresponding element in `array` is found in `search_list`.
    """
    if not search_list:
        return np.ones(array.shape, dtype=bool)
    else:
        return np.isin(array, search_list)


def get_stream_frames_generator(stream_source: str) -> Generator[np.ndarray, None, None]:
    """
    Generator function to yield frames from an RTSP stream.

    Args:
        stream_source (str): URL of the RTSP video stream.

    Yields:
        np.ndarray: The next frame from the video stream.
    """
    cap = cv2.VideoCapture(stream_source)
    if not cap.isOpened():
        raise Exception("Error: Could not open video stream.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of stream or error reading frame.")
                break
            yield frame
    finally:
        cap.release()


class FPSMonitor:
    """Clase para monitorear el rendimiento de fotogramas por segundo (FPS) en
    un proceso de video.
    Args:
        sample_size (int): El número máximo de observaciones para la evaluación
            del rendimiento de FPS.
    """
    def __init__(self, sample_size: int = 30):
        self.timestamps = deque(maxlen=sample_size)

    def fps(self) -> float:
        """Calcula el rendimiento de fotogramas por segundo (FPS) basado en los
        tiempos de las muestras almacenadas.
        Returns:
            float: El rendimiento de FPS calculado.
        """
        if not self.timestamps:
            return 0.0
        elapsed_time = self.timestamps[-1] - self.timestamps[0]
        
        return (len(self.timestamps)) / elapsed_time if elapsed_time != 0 else 0.0

    def tick(self) -> None:
        """Agrega un nuevo tiempo de muestra a la lista de tiempos.
        """
        self.timestamps.append(time.monotonic())