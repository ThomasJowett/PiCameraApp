import sys
import tkinter as tk
from tkinter import messagebox
from picamera2 import Picamera2, Preview

class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.picam2 = Picamera2()
        self.picam2.start_preview(Preview.QTGL)
        self.picam2.start()
        
        self.title("Camera App")
        #self.attributes('-fullscreen', True)
        
        self.capture_button = tk.Button(self, text="Take Picture", command=self.take_picture)
        self.capture_button.pack(expand=True)
        self.bind("<Escape>", self.exit_fullscreen)
        
    def take_picture(self):
        try:
            image = self.picam2.capture_file('./image.jpg')
            messagebox.showinfo("Success", "Image captured successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture image:\n{e}")
            
    def exit_fullscreen(self, event=None):
        self.attributes('-fullscreen', False)
        self.quit()
    
if __name__ == '__main__':
    app = CameraApp()
    app.mainloop()