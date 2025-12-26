"""Main application window."""
import tkinter as tk
from tkinter import messagebox, ttk

from ..models.user_session import UserSession
from ..models.virtual_camera import VirtualCamera
from ..services.camera_manager import CameraManagerService
from ..services.video_library import VideoLibraryService
from .camera_creator import CameraCreatorWidget
from .video_upload import VideoUploadWidget


class MainWindow:
    """Main application window."""
    
    def __init__(self, root, session: UserSession):
        """Initialize the main window.
        
        Args:
            root: Tkinter root window
            session: Authenticated user session
        """
        self.root = root
        self.session = session
        
        # Initialize services
        self.video_library = VideoLibraryService()
        self.camera_manager = CameraManagerService(self.video_library)
        
        # Setup window
        self.root.title("Virtual Camera Server")
        self.root.geometry("1000x700")
        
        # Create menu bar
        self._create_menu()
        
        # Create main content area with tabs
        self._create_content_area()
        
        # Refresh displays
        self._refresh_video_library()
        self._refresh_camera_list()
    
    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self._refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_content_area(self):
        """Create main content area with notebook tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Video Library
        video_tab = ttk.Frame(self.notebook)
        self.notebook.add(video_tab, text="Video Library")
        self._create_video_library_tab(video_tab)
        
        # Tab 2: Cameras
        camera_tab = ttk.Frame(self.notebook)
        self.notebook.add(camera_tab, text="Virtual Cameras")
        self._create_camera_tab(camera_tab)
    
    def _create_video_library_tab(self, parent):
        """Create video library tab."""
        # Upload section
        upload_frame = tk.LabelFrame(parent, text="Upload Video")
        upload_frame.pack(fill=tk.X, padx=10, pady=10)
        
        upload_widget = VideoUploadWidget(
            upload_frame,
            self.video_library,
            on_upload_callback=self._on_video_uploaded
        )
        upload_widget.get_widget().pack(fill=tk.X, padx=5, pady=5)
        
        # Video list section
        list_frame = tk.LabelFrame(parent, text="Video Library")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for video list
        columns = ("Filename", "Duration", "Size", "Format", "Dimensions")
        self.video_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.video_tree.heading("Filename", text="Filename")
        self.video_tree.heading("Duration", text="Duration (s)")
        self.video_tree.heading("Size", text="Size (MB)")
        self.video_tree.heading("Format", text="Format")
        self.video_tree.heading("Dimensions", text="Dimensions")
        
        self.video_tree.column("Filename", width=200)
        self.video_tree.column("Duration", width=100)
        self.video_tree.column("Size", width=100)
        self.video_tree.column("Format", width=80)
        self.video_tree.column("Dimensions", width=120)
        
        # Scrollbar
        video_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=video_scrollbar.set)
        
        # Pack
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        video_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_button = tk.Button(list_frame, text="Refresh", command=self._refresh_video_library)
        refresh_button.pack(pady=5)
    
    def _create_camera_tab(self, parent):
        """Create camera management tab."""
        # Left panel: Camera list
        left_panel = tk.Frame(parent)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Camera list section
        list_frame = tk.LabelFrame(left_panel, text="Virtual Cameras")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for camera list
        columns = ("Name", "Status", "Videos", "RTSP URL")
        self.camera_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.camera_tree.heading("Name", text="Camera Name")
        self.camera_tree.heading("Status", text="Status")
        self.camera_tree.heading("Videos", text="Videos")
        self.camera_tree.heading("RTSP URL", text="RTSP URL")
        
        self.camera_tree.column("Name", width=150)
        self.camera_tree.column("Status", width=80)
        self.camera_tree.column("Videos", width=80)
        self.camera_tree.column("RTSP URL", width=300)
        
        # Scrollbar
        camera_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.camera_tree.yview)
        self.camera_tree.configure(yscrollcommand=camera_scrollbar.set)
        
        # Pack
        self.camera_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        camera_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Camera controls
        controls_frame = tk.Frame(left_panel)
        controls_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = tk.Button(controls_frame, text="Start", command=self._start_camera, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(controls_frame, text="Stop", command=self._stop_camera, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        refresh_camera_button = tk.Button(controls_frame, text="Refresh", command=self._refresh_camera_list)
        refresh_camera_button.pack(side=tk.LEFT, padx=5)
        
        # Bind selection
        self.camera_tree.bind('<<TreeviewSelect>>', self._on_camera_selected)
        
        # Right panel: Camera creator
        right_panel = tk.Frame(parent)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        creator_frame = tk.LabelFrame(right_panel, text="Create New Camera")
        creator_frame.pack(fill=tk.BOTH, expand=True)
        
        creator_widget = CameraCreatorWidget(
            creator_frame,
            self.camera_manager,
            self.video_library,
            on_create_callback=self._on_camera_created
        )
        creator_widget.get_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _refresh_video_library(self):
        """Refresh the video library display."""
        # Clear existing items
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)
        
        # Load videos
        try:
            videos = self.video_library.list_videos()
            for video in videos:
                size_mb = video.file_size / (1024 * 1024)
                dimensions = f"{video.width}x{video.height}"
                self.video_tree.insert(
                    "",
                    tk.END,
                    values=(
                        video.filename,
                        f"{video.duration:.1f}",
                        f"{size_mb:.2f}",
                        video.format,
                        dimensions
                    ),
                    tags=(video.id,)
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load videos: {e}")
    
    def _refresh_camera_list(self):
        """Refresh the camera list display."""
        # Clear existing items
        for item in self.camera_tree.get_children():
            self.camera_tree.delete(item)
        
        # Load cameras
        try:
            cameras = self.camera_manager.list_cameras()
            for camera in cameras:
                video_count = len(camera.video_ids)
                self.camera_tree.insert(
                    "",
                    tk.END,
                    values=(
                        camera.name,
                        camera.status,
                        str(video_count),
                        camera.rtsp_url
                    ),
                    tags=(camera.id,)
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cameras: {e}")
    
    def _on_video_uploaded(self, video):
        """Callback when video is uploaded.
        
        Args:
            video: Uploaded Video object
        """
        self._refresh_video_library()
    
    def _on_camera_created(self, camera: VirtualCamera):
        """Callback when camera is created.
        
        Args:
            camera: Created VirtualCamera object
        """
        self._refresh_camera_list()
    
    def _on_camera_selected(self, event):
        """Handle camera selection.
        
        Args:
            event: Selection event
        """
        selection = self.camera_tree.selection()
        if selection:
            item = self.camera_tree.item(selection[0])
            camera_id = item['tags'][0] if item['tags'] else None
            
            if camera_id:
                try:
                    camera = self.camera_manager.get_camera(camera_id)
                    # Enable/disable buttons based on status
                    if camera.status == "active":
                        self.start_button.config(state=tk.DISABLED)
                        self.stop_button.config(state=tk.NORMAL)
                    else:
                        self.start_button.config(state=tk.NORMAL)
                        self.stop_button.config(state=tk.DISABLED)
                except Exception:
                    pass
    
    def _start_camera(self):
        """Start selected camera."""
        selection = self.camera_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a camera")
            return
        
        item = self.camera_tree.item(selection[0])
        camera_id = item['tags'][0] if item['tags'] else None
        
        if camera_id:
            try:
                from ..services.rtsp_server import get_rtsp_manager
                camera = self.camera_manager.get_camera(camera_id)
                rtsp_manager = get_rtsp_manager()
                rtsp_manager.start_stream(camera, self.video_library, self.camera_manager)
                
                messagebox.showinfo("Success", f"Camera '{camera.name}' started streaming")
                self._refresh_camera_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start camera: {e}")
                self._refresh_camera_list()
    
    def _stop_camera(self):
        """Stop selected camera."""
        selection = self.camera_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a camera")
            return
        
        item = self.camera_tree.item(selection[0])
        camera_id = item['tags'][0] if item['tags'] else None
        
        if camera_id:
            try:
                from ..services.rtsp_server import get_rtsp_manager
                camera = self.camera_manager.get_camera(camera_id)
                rtsp_manager = get_rtsp_manager()
                rtsp_manager.stop_stream(camera_id, self.camera_manager)
                
                messagebox.showinfo("Success", f"Camera '{camera.name}' stopped streaming")
                self._refresh_camera_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop camera: {e}")
                self._refresh_camera_list()
    
    def _refresh_all(self):
        """Refresh all displays."""
        self._refresh_video_library()
        self._refresh_camera_list()
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Virtual Camera Server\n\n"
            "A Python-based application for creating virtual cameras\n"
            "that stream videos via RTSP protocol.\n\n"
            "Version: 1.0.0"
        )

