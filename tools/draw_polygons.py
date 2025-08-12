import cv2
import json
import os
import numpy as np

class PolygonDrawer:
    def __init__(self, source):
        self.source = source
        self.points = []
        self.polygons = []
        self.current_polygon = []
        self.image = None
        self.window_name = "Polygon Drawer"
        self.loaded_polygons = []
        self.version = 1
        self.mouse_position = None  # Para rastrear la posición actual del mouse

        if os.path.isfile(source):
            if source.endswith(('.png', '.jpg', '.jpeg')):
                self.image = cv2.imread(source)
            else:
                self.cap = cv2.VideoCapture(source)
                ret, self.image = self.cap.read()
                if not ret:
                    print("Error reading video file")
                    exit()
        elif source.isdigit():
            self.cap = cv2.VideoCapture(int(source))
            ret, self.image = self.cap.read()
            if not ret:
                print("Error opening webcam")
                exit()
        else:
            self.cap = cv2.VideoCapture(source)
            ret, self.image = self.cap.read()
            if not ret:
                print("Error opening RTSP stream")
                exit()

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        # Cargar polígonos al inicio si existe un archivo JSON
        self.load_polygons()

        # Mostrar la imagen inmediatamente después de inicializar
        self.draw_polygon()

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.mouse_position = (x, y)  # Actualizar la posición del mouse
            self.draw_polygon()  # Redibujar la imagen con la línea dinámica

        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_polygon.append((x, y))
            self.mouse_position = None  # Reiniciar la posición del mouse después de hacer clic
            self.draw_polygon()

    def draw_polygon(self):
        temp_image = self.image.copy()

        # Dibujar polígonos cargados
        if self.loaded_polygons:
            for i, polygon in enumerate(self.loaded_polygons):
                cv2.polylines(temp_image, [polygon], True, (0, 255, 0), 2)
                cv2.putText(temp_image, str(i + 1), polygon[0], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Dibujar polígonos guardados
        if self.polygons:
            for i, polygon in enumerate(self.polygons):
                cv2.polylines(temp_image, [np.array(polygon, dtype=np.int32)], True, (0, 0, 255), 2)
                cv2.putText(temp_image, str(i + 1), polygon[0], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Dibujar el polígono actual
        if len(self.current_polygon) > 1:
            for i in range(1, len(self.current_polygon)):
                cv2.line(temp_image, self.current_polygon[i - 1], self.current_polygon[i], (0, 0, 255), 2)
            cv2.line(temp_image, self.current_polygon[-1], self.current_polygon[0], (0, 0, 255), 2)

        # Dibujar puntos del polígono actual
        for point in self.current_polygon:
            cv2.circle(temp_image, point, 5, (0, 0, 255), -1)

        # Dibujar la línea dinámica desde el último punto hasta la posición del mouse
        if self.mouse_position and len(self.current_polygon) > 0:
            cv2.line(temp_image, self.current_polygon[-1], self.mouse_position, (255, 0, 0), 2)

        cv2.imshow(self.window_name, temp_image)

    def run(self):
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 13:  # Enter key
                if len(self.current_polygon) > 2:
                    self.polygons.append(self.current_polygon)
                    self.current_polygon = []
                    self.draw_polygon()  # Actualizar la imagen con el polígono guardado
            elif key == ord('c'):  # Cancel current polygon
                self.current_polygon = []
                self.draw_polygon()
            elif key == ord('z'):  # Cancel last point
                if self.current_polygon:
                    self.current_polygon.pop()
                    self.draw_polygon()
            elif key == ord('s'):  # Save polygons to JSON
                self.save_polygons()
            elif key == ord('l'):  # Load polygons from JSON
                self.load_polygons()
            elif key == 27:  # ESC key
                break

        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()

    def save_polygons(self):
        if self.polygons:
            filename = f"polygons_v{self.version}.json"
            data = {}

            # Cargar el archivo JSON existente si existe
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)

            # Actualizar solo la llave "poligonos"
            data["poligonos"] = {}
            for i, polygon in enumerate(self.polygons):
                data["poligonos"][str(i + 1)] = polygon

            # Guardar el archivo JSON con las demás llaves intactas
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)  # indent=4 para formato legible
            print(f"Polygons saved to {filename}")
            self.version += 1

    def load_polygons(self):
        filename = "polygons_v1.json"
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                if "poligonos" in data:
                    self.loaded_polygons = [np.array(polygon, dtype=np.int32) for polygon in data["poligonos"].values()]
                    print(f"Polygons loaded from {filename}")
                else:
                    print(f"El archivo {filename} no contiene la llave 'poligonos'")
            self.draw_polygon()
        else:
            print(f"No se encontró el archivo {filename}")

if __name__ == "__main__":
    source = input("Enter image path, video path, webcam number, or RTSP stream URL: ")
    drawer = PolygonDrawer(source)
    drawer.run()