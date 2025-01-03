import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from datetime import datetime, timedelta
import os
import time

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
        except Exception as e:
            self.image_captured.emit(f"Error: {e}")
            
class CameraApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.picam2 = Picamera2()
        self.capture_config = self.picam2.create_still_configuration()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (800, 480)}))

        # Create the Qt preview window
        self.qpicamera2 = QGlPicamera2(self.picam2, width=800, height=480, keep_ar=False)
        self.qpicamera2.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # Make it frameless

        self.setCentralWidget(self.qpicamera2)
        self.setWindowState(QtCore.Qt.WindowFullScreen)  # Set to fullscreen
        
        # Start the camera preview
        self.picam2.start()
        
        # Create a button to take pictures
        self.capture_button = QtWidgets.QPushButton("Take Picture", self)
        self.capture_button.setFixedSize(200, 50)  # Set button size
        self.capture_button.clicked.connect(self.take_picture)
        self.statusBar().addPermanentWidget(self.capture_button)  # Add button to status bar

        self.show()
        
        self.capture_thread = None

    def take_picture(self):
        self.capture_button.setEnabled(False)
        self.capture_thread = CaptureThread(self.picam2)
        self.capture_thread.image_captured.connect(self.on_image_captured)
        self.capture_thread.start()
        
    def on_image_captured(self, filepath):
        self.capture_button.setEnabled(True)
        if filepath.startswith("Error:"):
           QtWidgets.QMessageBox.critical(self, "Error", filepath)
        else:
           QtWidgets.QMessageBox.information(self, "Image Saved", f"Image saved as: {filepath}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CameraApp()
    sys.exit(app.exec_())
