import pyautogui
import tkinter as tk
from tkinter import messagebox, StringVar
import os
from PIL import Image, ImageTk, ImageGrab
import threading
import time

class ScreenshotApp:
    def __init__(self, root):  # Fixed method name with double underscores
        self.root = root
        self.root.title("Screenshot App")
        self.root.geometry("300x250")  # Increased height to accommodate the new field
        self.root.resizable(False, False)
        
        self.screenshot_count = 0
        self.running = False
        # Change save directory to the specified folder
        self.save_dir = r"C:\Users\adnan\OneDrive\Desktop\FYDP\Chapter-9\English"
        self.selection_in_progress = False
        
        # Create screenshots directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        # Create GUI elements
        self.title_label = tk.Label(root, text="Screenshot Application", font=("Arial", 14, "bold"))
        self.title_label.pack(pady=10)
        
        # Add counter input frame
        counter_frame = tk.Frame(root)
        counter_frame.pack(pady=5)
        
        counter_label = tk.Label(counter_frame, text="Example-")
        counter_label.pack(side=tk.LEFT)
        
        self.counter_var = StringVar(value="1")  # Default value
        self.counter_entry = tk.Entry(counter_frame, textvariable=self.counter_var, width=5)
        self.counter_entry.pack(side=tk.LEFT, padx=5)
        
        self.info_label = tk.Label(root, text="Press the button to start.\nThen use F6 to select a region.\nPress Esc to quit.")
        self.info_label.pack(pady=5)
        
        self.status_label = tk.Label(root, text="Status: Idle", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        self.start_button = tk.Button(root, text="Take Screenshot", command=self.capture_area)
        self.start_button.pack(pady=10)
        
        self.quit_button = tk.Button(root, text="Quit", command=self.on_close)
        self.quit_button.pack(pady=5)
        
        # Set up protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def capture_area(self):
        if self.selection_in_progress:
            return
        
        # Get the starting number from the entry field
        try:
            self.screenshot_count = int(self.counter_var.get()) - 1  # Subtract 1 since it will be incremented before use
            if self.screenshot_count < 0:
                self.screenshot_count = 0
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
            return
            
        self.selection_in_progress = True
        self.root.withdraw()  # Hide the main window during capture
        time.sleep(0.2)  # Small delay to ensure window is hidden
        
        try:
            # Create overlay window for selection
            self.overlay = tk.Toplevel()
            self.overlay.attributes('-fullscreen', True)
            self.overlay.attributes('-alpha', 0.3)  # Semi-transparent
            self.overlay.attributes('-topmost', True)
            
            # Take a screenshot to display as background
            screen = pyautogui.screenshot()
            self.tk_screen = ImageTk.PhotoImage(screen)
            
            # Create canvas for selection
            self.canvas = tk.Canvas(self.overlay, cursor="cross", highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.create_image(0, 0, image=self.tk_screen, anchor=tk.NW)
            
            # Variables for selection coordinates
            self.start_x = None
            self.start_y = None
            self.rect = None
            
            # Bind canvas events
            self.canvas.bind("<ButtonPress-1>", self.on_press)
            self.canvas.bind("<B1-Motion>", self.on_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_release)
            self.canvas.bind("<Escape>", lambda e: self.cancel_selection())
            
            # Make canvas focusable
            self.canvas.focus_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize screen capture: {e}")
            self.selection_in_progress = False
            self.root.deiconify()  # Show main window again
    
    def on_press(self, event):
        # Save starting position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # Create rectangle if it doesn't exist
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2)
    
    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        # Update rectangle size
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
    
    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # Ensure coordinates are in the right order
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        
        # Check if selection is too small
        if x2 - x1 < 10 or y2 - y1 < 10:
            messagebox.showinfo("Selection too small", "Please select a larger area")
            self.cancel_selection()
            return
        
        # Take the screenshot of the selected area
        self.take_screenshot(int(x1), int(y1), int(x2), int(y2))
        
        # Close overlay
        self.overlay.destroy()
        self.selection_in_progress = False
        self.root.deiconify()  # Show main window again
    
    def cancel_selection(self):
        if hasattr(self, 'overlay'):
            self.overlay.destroy()
        self.selection_in_progress = False
        self.root.deiconify()
    
    def take_screenshot(self, x1, y1, x2, y2):
        try:
            self.screenshot_count += 1
            filename = f"Example-{self.screenshot_count}.png"
            filepath = os.path.join(self.save_dir, filename)
            
            # Capture the selected region
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            screenshot.save(filepath)
            
            # Update status with notification
            self.status_label.config(text=f"Status: Saved {filename}")
            
            # Update the counter entry field to show the next number
            self.counter_var.set(str(self.screenshot_count + 1))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {e}")
    
    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

if __name__ == "__main__":  # Fixed with double underscores
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()