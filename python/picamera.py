import sys
import os
import tkinter as tk
from tkinter import messagebox
from picamera2 import Picamera2, Preview
from datetime import datetime

pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures")

os.makedirs(pictures_folder, exist_ok=True)

class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.picam2 = Picamera2()
        preview_config = self.picam2.create_preview_configuration(main={"size":(640, 480)})
        self.capture_config = self.picam2.create_still_configuration()
        self.picam2.configure(preview_config)
        #self.picam2.start_preview(Preview.QTGL, fullscreen=True)
        self.picam2.start_preview(Preview.QTGL)
        self.picam2.start()
        
        self.title("Camera App")
        #self.frame = tk.Frame(self)
        #self.frame.pack(fill="both", expand=True)
        
        self.capture_button = tk.Button(self, text="Take Picture", command=self.take_picture,
                                        font=("Ariel", 16),
                                        width=10, height=3)
        self.capture_button.pack(side="right", fill="both", expand=True)
        #self.attributes("-topmost", True)
        #self.attributes("-fullscreen", True)
        self.bind("<Escape>", self.exit_fullscreen)
        
    def take_picture(self):
        try:
            image = self.picam2.switch_mode_and_capture_image(self.capture_config)
            request = self.picam2.capture_request()
            metadata = request.get_metadata()
            
            sensor_timestamp_ns = metadata['SensorTimestamp']
            timestamp = datetime.fromtimestamp(sensor_timestamp_ns / 1e9)
            
            filename_timestamp = timestamp.strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_timestamp}.jpg"
            filepath = os.path.join(pictures_folder, filename)
            
            image.save(filepath)
            
            request.release()
            print(f"Image saved as: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture image:\n{e}")
            
    def exit_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)
        self.quit()
        
    def close(self):
        self.picam2.close()
        self.destroy()
    
if __name__ == '__main__':
    app = CameraApp()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.close()