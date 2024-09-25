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
        self.picam2.start_preview(Preview.QTGL, x=0, y=0)
        self.picam2.start()
        
        self.title("Camera App")
        #self.attributes('-fullscreen', True)
        
        self.capture_button = tk.Button(self, text="Take Picture", command=self.take_picture)
        self.capture_button.pack(expand=True)
        self.bind("<Escape>", self.exit_fullscreen)
        
    def take_picture(self):
        try:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{current_time}.jpg"
            filepath = os.path.join(pictures_folder, filename)
            image = self.picam2.switch_mode_and_capture_image(self.capture_config)
            print(f"Image saved as: {filepath}")
            image.save(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture image:\n{e}")
            
    def exit_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)
        self.quit()
        
    def close(self):
        self.picam2.close()
        self.master.destroy()
    
if __name__ == '__main__':
    app = CameraApp()
    try:
        app.mainloop()
    except KeyboardInterupt:
        app.close()