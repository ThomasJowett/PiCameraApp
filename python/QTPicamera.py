import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2
from datetime import datetime
import os

pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures")
os.makedirs(pictures_folder, exist_ok=True)

class CameraApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.picam2 = Picamera2()
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

    def take_picture(self):
        try:
            image = self.picam2.switch_mode_and_capture_image()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(pictures_folder, filename)
            image.save(filepath)
            print(f"Image saved as: {filepath}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to capture image:\n{e}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CameraApp()
    sys.exit(app.exec_())
