"""Video upload interface component."""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..services.exceptions import InvalidVideoError, StorageError
from ..services.video_library import VideoLibraryService


class VideoUploadWidget:
    """Widget for uploading videos to the library."""
    
    def __init__(self, parent, video_library_service: VideoLibraryService, on_upload_callback=None):
        """Initialize the video upload widget.
        
        Args:
            parent: Parent tkinter widget
            video_library_service: VideoLibraryService instance
            on_upload_callback: Optional callback function called after successful upload
        """
        self.parent = parent
        self.video_library = video_library_service
        self.on_upload_callback = on_upload_callback
        
        # Create frame
        self.frame = tk.Frame(parent)
        
        # Upload button
        self.upload_button = tk.Button(
            self.frame,
            text="Upload Video",
            command=self._upload_video,
            width=20
        )
        self.upload_button.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.frame, text="", fg="green")
        self.status_label.pack(pady=5)
    
    def get_widget(self):
        """Get the tkinter widget.
        
        Returns:
            tk.Frame: The widget frame
        """
        return self.frame
    
    def _upload_video(self):
        """Handle video upload."""
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Get filename
        import os
        filename = os.path.basename(file_path)
        
        # Update status
        self.status_label.config(text=f"Uploading {filename}...", fg="blue")
        self.frame.update()
        
        try:
            # Upload video
            video = self.video_library.upload_video(file_path, filename)
            
            # Success message
            self.status_label.config(
                text=f"Uploaded: {video.filename} ({video.duration:.1f}s)",
                fg="green"
            )
            
            # Call callback if provided
            if self.on_upload_callback:
                self.on_upload_callback(video)
            
            messagebox.showinfo("Success", f"Video uploaded successfully: {video.filename}")
            
        except InvalidVideoError as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Invalid video file: {e}")
        except StorageError as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Storage error: {e}")
        except Exception as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Upload failed: {e}")

