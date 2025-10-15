import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from datetime import datetime, timedelta
import os
import time
import cv2
import numpy as np

pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures")
os.makedirs(pictures_folder, exist_ok=True)

class CaptureThread(QtCore.QThread):
    image_captured = QtCore.pyqtSignal(str)
    
    def __init__(self, picam2, parent=None):
        super().__init__(parent)
        self.picam2 = picam2
        self.capture_config = self.picam2.create_still_configuration()
        
    def run(self):
        try:
            image = self.picam2.switch_mode_and_capture_image(self.capture_config)
            request = self.picam2.capture_request()
            metadata = request.get_metadata()
            sensor_timestamp_ns = metadata['SensorTimestamp']
            uptime_s = time.clock_gettime(time.CLOCK_MONOTONIC)
            boot_time = datetime.now() - timedelta(seconds=uptime_s)
            timestamp = boot_time + timedelta(seconds = sensor_timestamp_ns / 1e9)
            filename_timestamp = timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_timestamp}.jpg"
            filepath = os.path.join(pictures_folder, filename)
            image.save(filepath)
            print(f"Image saved as: {filepath}")
            self.image_captured.emit(filepath)
            request.release()
        except Exception as e:
            self.image_captured.emit(f"Error: {e}")

class SharpnessThread(QtCore.QThread):
    sharpness_updated = QtCore.pyqtSignal(float)

    def __init__(self, picam2, interval = 1.0, parent=None):
        super().__init__(parent)
        self.picam2 = picam2
        self.running = True
        self.interval = interval
    
    def run(self):
        while self.running:
            try:
                image = self.picam2.capture_array()

                if image is None:
                    continue
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                h, w = gray.shape
                cx, cy = w // 2, h // 2
                size_x, size_y = w // 6, h // 6
                crop = gray[cy - size_y:cy + size_y, cx - size_x:cx + size_x]
                laplacian = cv2.Laplacian(crop, cv2.CV_64F).var()
                sharpness = min(100, laplacian / 100.0)
                self.sharpness_updated.emit(sharpness)
            except Exception as e:
                print(f"Error calculating sharpness: {e}")
            self.msleep(int(self.interval * 1000))

    def stop(self):
        self.running = False
        self.wait()
class CameraApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.picam2 = Picamera2()

        # Detect the screen size and set the preview size accordingly
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        width, height = screen_size.width(), screen_size.height() - 75
        self.capture_config = self.picam2.create_still_configuration()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (width, height)}))

        # Create the Qt preview window
        self.qpicamera2 = QGlPicamera2(self.picam2, width=width, height=height, keep_ar=True)
        self.qpicamera2.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Make it frameless

        self.setCentralWidget(self.qpicamera2)
        self.setWindowState(QtCore.Qt.WindowFullScreen)  # Set to fullscreen
        
        # Start the camera preview
        self.picam2.start()

        # Start the sharpness monitoring thread
        self.sharpness_thread = SharpnessThread(self.picam2)
        self.sharpness_thread.sharpness_updated.connect(self.update_sharpness_display)
        self.sharpness_thread.start()
        
        # Create a container for button and label        
        button_container = QtWidgets.QWidget(self)
        button_layout = QtWidgets.QHBoxLayout(button_container)
        
        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        
        # Create a button to take pictures
        self.capture_button = QtWidgets.QPushButton("Take Picture", self)
        self.capture_button.setFixedSize(200, 50)  # Set button size
        self.capture_button.clicked.connect(self.take_picture)
        
        # Create a label for displaying the focus
        self.filepath_label = QtWidgets.QLabel("", self)
        self.filepath_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        button_layout.addWidget(self.filepath_label)
        button_layout.addWidget(self.exit_button)
        button_layout.addWidget(self.capture_button)
        self.statusBar().addPermanentWidget(button_container)  # Add button to status bar
        
        self.show()
        
        self.capture_thread = None
        self.image_process_thread = None

    def take_picture(self):
        self.capture_button.setEnabled(False)
        self.filepath_label.setText("")
        self.capture_thread = CaptureThread(self.picam2)
        self.capture_thread.image_captured.connect(self.on_image_captured)
        self.capture_thread.start()
        
    def on_image_captured(self, filepath):
        self.capture_button.setEnabled(True)
        if filepath.startswith("Error:"):
           QtWidgets.QMessageBox.critical(self, "Error", filepath)
        else:
           self.filepath_label.setText(f"{filepath}")

    def closeEvent(self, event):
        if hasattr(self, "sharpness_thread"):
            self.sharpness_thread.stop()
        self.picam2.stop()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CameraApp()
    sys.exit(app.exec_())
