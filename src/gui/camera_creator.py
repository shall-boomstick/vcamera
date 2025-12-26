"""Camera creator interface component."""
import tkinter as tk
from tkinter import messagebox, ttk

from ..models.video import Video
from ..services.camera_manager import CameraManagerService
from ..services.exceptions import DuplicateNameError, InvalidAuthError, VideoNotFoundError
from ..services.video_library import VideoLibraryService


class CameraCreatorWidget:
    """Widget for creating virtual cameras."""
    
    def __init__(
        self,
        parent,
        camera_manager: CameraManagerService,
        video_library: VideoLibraryService,
        on_create_callback=None
    ):
        """Initialize the camera creator widget.
        
        Args:
            parent: Parent tkinter widget
            camera_manager: CameraManagerService instance
            video_library: VideoLibraryService instance
            on_create_callback: Optional callback function called after successful creation
        """
        self.parent = parent
        self.camera_manager = camera_manager
        self.video_library = video_library
        self.on_create_callback = on_create_callback
        
        # Create frame
        self.frame = tk.Frame(parent)
        
        # Camera name
        name_frame = tk.Frame(self.frame)
        name_frame.pack(pady=5, fill=tk.X)
        tk.Label(name_frame, text="Camera Name:").pack(side=tk.LEFT, padx=5)
        self.name_entry = tk.Entry(name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        # Video selection
        video_frame = tk.Frame(self.frame)
        video_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        tk.Label(video_frame, text="Select Videos:").pack(anchor=tk.W, padx=5)
        
        # Listbox with scrollbar for video selection
        listbox_frame = tk.Frame(video_frame)
        listbox_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=5)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.video_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.video_listbox.yview)
        
        # Refresh button for video list
        refresh_button = tk.Button(video_frame, text="Refresh Video List", command=self._refresh_videos)
        refresh_button.pack(pady=5)
        
        # Authentication section
        auth_frame = tk.LabelFrame(self.frame, text="RTSP Authentication (Optional)")
        auth_frame.pack(pady=10, fill=tk.X, padx=5)
        
        self.auth_enabled_var = tk.BooleanVar()
        auth_checkbox = tk.Checkbutton(auth_frame, text="Enable Authentication", variable=self.auth_enabled_var)
        auth_checkbox.pack(anchor=tk.W, padx=5, pady=5)
        
        # Username field
        username_frame = tk.Frame(auth_frame)
        username_frame.pack(pady=5, fill=tk.X, padx=5)
        tk.Label(username_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        self.auth_username_entry = tk.Entry(username_frame, width=25)
        self.auth_username_entry.pack(side=tk.LEFT, padx=5)
        self.auth_username_entry.config(state=tk.DISABLED)
        
        # Password field
        password_frame = tk.Frame(auth_frame)
        password_frame.pack(pady=5, fill=tk.X, padx=5)
        tk.Label(password_frame, text="Password:").pack(side=tk.LEFT, padx=5)
        self.auth_password_entry = tk.Entry(password_frame, width=25, show="*")
        self.auth_password_entry.pack(side=tk.LEFT, padx=5)
        self.auth_password_entry.config(state=tk.DISABLED)
        
        # Enable/disable auth fields based on checkbox
        def toggle_auth_fields():
            state = tk.NORMAL if self.auth_enabled_var.get() else tk.DISABLED
            self.auth_username_entry.config(state=state)
            self.auth_password_entry.config(state=state)
        
        self.auth_enabled_var.trace('w', lambda *args: toggle_auth_fields())
        
        # Create button
        self.create_button = tk.Button(
            self.frame,
            text="Create Camera",
            command=self._create_camera,
            width=20
        )
        self.create_button.pack(pady=10)
        
        # Status label
        self.status_label = tk.Label(self.frame, text="", fg="green")
        self.status_label.pack(pady=5)
        
        # Load videos initially
        self._refresh_videos()
    
    def get_widget(self):
        """Get the tkinter widget.
        
        Returns:
            tk.Frame: The widget frame
        """
        return self.frame
    
    def _refresh_videos(self):
        """Refresh the video list."""
        self.video_listbox.delete(0, tk.END)
        try:
            videos = self.video_library.list_videos()
            for video in videos:
                display_text = f"{video.filename} ({video.duration:.1f}s)"
                self.video_listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load videos: {e}")
    
    def _create_camera(self):
        """Handle camera creation."""
        # Get camera name
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a camera name")
            return
        
        # Get selected videos
        selected_indices = self.video_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one video")
            return
        
        # Get video IDs
        videos = self.video_library.list_videos()
        video_ids = [videos[i].id for i in selected_indices]
        
        # Get auth settings
        auth_enabled = self.auth_enabled_var.get()
        auth_username = None
        auth_password = None
        
        if auth_enabled:
            auth_username = self.auth_username_entry.get().strip()
            auth_password = self.auth_password_entry.get()
            
            if not auth_username or not auth_password:
                messagebox.showerror("Error", "Please enter username and password for authentication")
                return
        
        # Update status
        self.status_label.config(text="Creating camera...", fg="blue")
        self.frame.update()
        
        try:
            # Create camera
            camera = self.camera_manager.create_camera(
                name=name,
                video_ids=video_ids,
                auth_enabled=auth_enabled,
                auth_username=auth_username,
                auth_password=auth_password
            )
            
            # Success message
            self.status_label.config(text=f"Created: {camera.name}", fg="green")
            
            # Clear form
            self.name_entry.delete(0, tk.END)
            self.video_listbox.selection_clear(0, tk.END)
            self.auth_enabled_var.set(False)
            self.auth_username_entry.delete(0, tk.END)
            self.auth_password_entry.delete(0, tk.END)
            
            # Call callback if provided
            if self.on_create_callback:
                self.on_create_callback(camera)
            
            messagebox.showinfo("Success", f"Camera created successfully: {camera.name}")
            
        except DuplicateNameError as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Camera name already exists: {e}")
        except VideoNotFoundError as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Video not found: {e}")
        except InvalidAuthError as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Invalid authentication configuration: {e}")
        except Exception as e:
            self.status_label.config(text="", fg="green")
            messagebox.showerror("Error", f"Failed to create camera: {e}")

