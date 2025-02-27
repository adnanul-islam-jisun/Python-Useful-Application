import os
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import glob

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Image Editor")
        self.root.geometry("800x600")
        
        # Variables
        self.current_image_path = None
        self.image_paths = []
        self.current_index = -1
        self.original_image = None
        self.edited_image = None
        self.display_image = None
        self.brush_size = 10
        self.is_drawing = False
        self.last_x, self.last_y = 0, 0
        self.zoom_level = 1.0  # Added zoom level tracking
        
        # UI Components
        self.create_ui()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Add keyboard shortcuts
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.reset_zoom())

    def create_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame (top)
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Open folder button
        self.open_btn = tk.Button(control_frame, text="Open Folder", command=self.open_folder)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        # Brush size slider
        tk.Label(control_frame, text="Brush Size:").pack(side=tk.LEFT, padx=5)
        self.size_slider = tk.Scale(control_frame, from_=1, to=50, orient=tk.HORIZONTAL, command=self.update_brush_size)
        self.size_slider.set(self.brush_size)
        self.size_slider.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        zoom_frame = tk.Frame(control_frame)
        zoom_frame.pack(side=tk.LEFT, padx=10)
        
        self.zoom_out_btn = tk.Button(zoom_frame, text="➖", command=self.zoom_out, width=2)
        self.zoom_out_btn.pack(side=tk.LEFT)
        
        self.zoom_label = tk.Label(zoom_frame, text="100%", width=5)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        self.zoom_in_btn = tk.Button(zoom_frame, text="➕", command=self.zoom_in, width=2)
        self.zoom_in_btn.pack(side=tk.LEFT)
        
        self.zoom_reset_btn = tk.Button(zoom_frame, text="Reset", command=self.reset_zoom)
        self.zoom_reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Save button
        self.save_btn = tk.Button(control_frame, text="Save", command=self.save_image)
        self.save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Navigation frame (bottom)
        nav_frame = tk.Frame(main_frame)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Previous button
        self.prev_btn = tk.Button(nav_frame, text="Previous", command=self.previous_image)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        # Image counter label
        self.counter_label = tk.Label(nav_frame, text="0/0")
        self.counter_label.pack(side=tk.LEFT, padx=5, expand=True)
        
        # Next button
        self.next_btn = tk.Button(nav_frame, text="Next", command=self.next_image)
        self.next_btn.pack(side=tk.RIGHT, padx=5)
        
        # Canvas for image display
        self.canvas_frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="gray", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Bind mouse events for drawing
        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        
        # Update UI state
        self.update_ui_state()
    
    def open_folder(self):
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if not folder_path:
            return
            
        # Get supported image formats
        image_extensions = ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.tiff")
        self.image_paths = []
        
        for ext in image_extensions:
            self.image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
        
        self.image_paths.sort()
        
        if self.image_paths:
            self.current_index = 0
            self.load_current_image()
        else:
            messagebox.showinfo("No Images", "No supported images found in this folder")
    
    def load_current_image(self):
        if 0 <= self.current_index < len(self.image_paths):
            # Save previous image if it exists
            if self.edited_image and self.current_image_path:
                self.save_current_image()
                
            self.current_image_path = self.image_paths[self.current_index]
            self.original_image = Image.open(self.current_image_path)
            self.edited_image = self.original_image.copy()
            self.display_image_on_canvas()
            self.update_ui_state()
    
    def display_image_on_canvas(self):
        if self.edited_image:
            self.canvas.delete("all")
            
            # Apply zoom
            if self.zoom_level != 1.0:
                # Calculate new dimensions
                new_width = int(self.edited_image.width * self.zoom_level)
                new_height = int(self.edited_image.height * self.zoom_level)
                
                # Create a resized version for display
                resized_image = self.edited_image.resize((new_width, new_height), Image.LANCZOS)
                self.display_image = ImageTk.PhotoImage(resized_image)
            else:
                # Use original size
                self.display_image = ImageTk.PhotoImage(self.edited_image)
            
            # Update canvas size to match the image dimensions
            self.canvas.config(scrollregion=(0, 0, 
                                           self.edited_image.width * self.zoom_level,
                                           self.edited_image.height * self.zoom_level))
            
            # Display image
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.display_image)
    
    def update_brush_size(self, val):
        self.brush_size = int(val)
    
    def start_draw(self, event):
        self.is_drawing = True
        # Convert canvas coordinates to image coordinates
        self.last_x = self.canvas.canvasx(event.x) / self.zoom_level
        self.last_y = self.canvas.canvasy(event.y) / self.zoom_level
    
    def draw(self, event):
        if not self.is_drawing or not self.edited_image:
            return
        
        # Convert canvas coordinates to image coordinates (accounting for zoom)
        x = self.canvas.canvasx(event.x) / self.zoom_level
        y = self.canvas.canvasy(event.y) / self.zoom_level
        
        # Draw on the image (using original image coordinates)
        draw = ImageDraw.Draw(self.edited_image)
        draw.line([self.last_x, self.last_y, x, y], fill="white", width=self.brush_size)
        
        # Also draw a circle at each point for better coverage
        draw.ellipse([x-self.brush_size/2, y-self.brush_size/2, 
                     x+self.brush_size/2, y+self.brush_size/2], fill="white")
        
        # Update display
        self.display_image_on_canvas()
        
        # Update position for next move
        self.last_x = x
        self.last_y = y
    
    def stop_draw(self, event):
        self.is_drawing = False
    
    def save_current_image(self):
        if self.edited_image and self.current_image_path:
            # Save directly to the original file path, overwriting it
            try:
                self.edited_image.save(self.current_image_path)
                # Show a brief notification in status and title
                self.root.title(f"Simple Image Editor - Saved: {os.path.basename(self.current_image_path)}")
                # Optional: Add a status message display somewhere in the UI
                print(f"Image automatically saved to: {self.current_image_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save image: {e}")
    
    def save_image(self):
        if self.edited_image:
            # Use current filename as default if available
            initial_file = ""
            if self.current_image_path:
                initial_file = os.path.basename(self.current_image_path)
                
            save_path = filedialog.asksaveasfilename(
                initialfile=initial_file,
                defaultextension=".png",
                filetypes=[("PNG files", ".png"), ("JPEG files", ".jpg"), ("All files", ".*")]
            )
            if save_path:
                self.edited_image.save(save_path)
                messagebox.showinfo("Success", "Image saved successfully")
    
    def next_image(self):
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            # Save the current image before moving to the next
            if self.edited_image:
                self.save_current_image()
                
            self.current_index += 1
            self.load_current_image()
    
    def previous_image(self):
        if self.image_paths and self.current_index > 0:
            # Save the current image before moving to the previous
            if self.edited_image:
                self.save_current_image()
                
            self.current_index -= 1
            self.load_current_image()
    
    def update_ui_state(self):
        # Update counter
        if self.image_paths:
            self.counter_label.config(text=f"{self.current_index + 1}/{len(self.image_paths)}")
        else:
            self.counter_label.config(text="0/0")
        
        # Enable/disable buttons
        if not self.image_paths:
            self.next_btn.config(state=tk.DISABLED)
            self.prev_btn.config(state=tk.DISABLED)
            self.save_btn.config(state=tk.DISABLED)
        else:
            self.save_btn.config(state=tk.NORMAL)
            self.next_btn.config(state=tk.NORMAL if self.current_index < len(self.image_paths) - 1 else tk.DISABLED)
            self.prev_btn.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
    
    def on_close(self):
        # Save the current image before closing without asking
        if self.edited_image and self.current_image_path:
            self.save_current_image()
        
        self.root.destroy()
    
    # Add zoom functionality methods
    def zoom_in(self):
        if self.edited_image:
            self.zoom_level = min(5.0, self.zoom_level * 1.25)  # Max zoom level of 500%
            self.update_zoom_label()
            self.display_image_on_canvas()
    
    def zoom_out(self):
        if self.edited_image:
            self.zoom_level = max(0.1, self.zoom_level / 1.25)  # Min zoom level of 10%
            self.update_zoom_label()
            self.display_image_on_canvas()
    
    def reset_zoom(self):
        if self.edited_image:
            self.zoom_level = 1.0
            self.update_zoom_label()
            self.display_image_on_canvas()
    
    def update_zoom_label(self):
        zoom_percentage = int(self.zoom_level * 100)
        self.zoom_label.config(text=f"{zoom_percentage}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.mainloop()