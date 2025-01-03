import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from datetime import datetime, timedelta
import os
import time
import cv2

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

class ImageProcess(QtCore.QThread):
    metadata_captured = QtCore.pyqtSignal(float)
    
    def __init__(self, picam2, parent=None):
        super().__init__(parent)
        self.picam2 = picam2
        
    def run(self):
        try:
            im = self.picam2.capture_array()
            gray_image = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
            variance = laplacian.var()
            focus_value = variance
            print(focus_value)
            self.metadata_captured.emit(focus_value)
        except Exception as e:
            self.metadata_captured.emit(0.0)

            
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
        
        # Create a container for button and label
        button_container = QtWidgets.QWidget(self)
        button_layout = QtWidgets.QHBoxLayout(button_container)
        
        # Create a button to take pictures
        self.capture_button = QtWidgets.QPushButton("Take Picture", self)
        self.capture_button.setFixedSize(200, 50)  # Set button size
        self.capture_button.clicked.connect(self.take_picture)
        
        # Create a label for displaying the focus
        self.focus_label = QtWidgets.QLabel("", self)
        self.focus_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        
        button_layout.addWidget(self.focus_label)
        button_layout.addWidget(self.capture_button)
        self.statusBar().addPermanentWidget(button_container)  # Add button to status bar
        
        #self.focus_timer = QtCore.QTimer(self)
        #self.focus_timer.timeout.connect(self.update_metadata)
        #self.focus_timer.start(500)

        self.show()
        
        self.capture_thread = None
        self.image_process_thread = None

    def take_picture(self):
        self.capture_button.setEnabled(False)
        self.focus_label.setText("")
        self.capture_thread = CaptureThread(self.picam2)
        self.capture_thread.image_captured.connect(self.on_image_captured)
        self.capture_thread.start()
        
    def on_image_captured(self, filepath):
        self.capture_button.setEnabled(True)
        if filepath.startswith("Error:"):
           QtWidgets.QMessageBox.critical(self, "Error", filepath)
        else:
           self.focus_label.setText(f"{filepath}")
           
    def on_metadata_captured(self, focus_value):
        self.focus_label.setText(f"Focus: {focus_value}")
    
    def update_metadata(self):
        try:
            self.image_process_thread = ImageProcess(self.picam2)
            self.image_process_thread.metadata_captured.connect(self.on_metadata_captured)
            self.image_process_thread.start()
        except Exception as e:
            print(f"Error updating focus: {e}")
            self.focus_label.setText("Focus: Error")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CameraApp()
    sys.exit(app.exec_())
