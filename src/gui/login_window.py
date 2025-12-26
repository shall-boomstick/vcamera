"""Login window for user authentication."""
import tkinter as tk
from tkinter import messagebox, ttk

from ..services.auth import AuthService
from ..services.exceptions import AuthenticationError, CredentialsNotFoundError


class LoginWindow:
    """Login window for user authentication."""
    
    def __init__(self, root, on_success_callback):
        """Initialize the login window.
        
        Args:
            root: Tkinter root window
            on_success_callback: Callback function called with UserSession on successful login
        """
        self.root = root
        self.on_success_callback = on_success_callback
        self.auth_service = AuthService()
        
        # Check if credentials exist
        if not self.auth_service.credentials_exist():
            self._show_create_credentials_dialog()
        else:
            self._show_login_dialog()
    
    def _show_create_credentials_dialog(self):
        """Show dialog to create initial credentials."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Credentials")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Username field
        tk.Label(dialog, text="Username:").pack(pady=5)
        username_entry = tk.Entry(dialog, width=30)
        username_entry.pack(pady=5)
        username_entry.focus()
        
        # Password field
        tk.Label(dialog, text="Password:").pack(pady=5)
        password_entry = tk.Entry(dialog, width=30, show="*")
        password_entry.pack(pady=5)
        
        # Confirm password field
        tk.Label(dialog, text="Confirm Password:").pack(pady=5)
        confirm_entry = tk.Entry(dialog, width=30, show="*")
        confirm_entry.pack(pady=5)
        
        def create_credentials():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username:
                messagebox.showerror("Error", "Username cannot be empty")
                return
            
            if not password:
                messagebox.showerror("Error", "Password cannot be empty")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            try:
                self.auth_service.create_credentials(username, password)
                messagebox.showinfo("Success", "Credentials created successfully. Please login.")
                dialog.destroy()
                self._show_login_dialog()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create credentials: {e}")
        
        # Create button
        tk.Button(dialog, text="Create Credentials", command=create_credentials).pack(pady=10)
        
        # Bind Enter key
        confirm_entry.bind('<Return>', lambda e: create_credentials())
    
    def _show_login_dialog(self):
        """Show login dialog."""
        # Clear root window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.title("Virtual Camera Server - Login")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Title
        title_label = tk.Label(self.root, text="Virtual Camera Server", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Username field
        username_frame = tk.Frame(self.root)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:").pack(side=tk.LEFT, padx=5)
        username_entry = tk.Entry(username_frame, width=25)
        username_entry.pack(side=tk.LEFT, padx=5)
        username_entry.focus()
        
        # Password field
        password_frame = tk.Frame(self.root)
        password_frame.pack(pady=10)
        tk.Label(password_frame, text="Password:").pack(side=tk.LEFT, padx=5)
        password_entry = tk.Entry(password_frame, width=25, show="*")
        password_entry.pack(side=tk.LEFT, padx=5)
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get()
            
            if not username:
                messagebox.showerror("Error", "Please enter username")
                return
            
            if not password:
                messagebox.showerror("Error", "Please enter password")
                return
            
            try:
                session = self.auth_service.authenticate(username, password)
                self.on_success_callback(session)
            except CredentialsNotFoundError:
                messagebox.showerror("Error", "No credentials found. Please create credentials first.")
            except AuthenticationError:
                messagebox.showerror("Error", "Invalid username or password")
            except Exception as e:
                messagebox.showerror("Error", f"Login failed: {e}")
        
        # Login button
        login_button = tk.Button(self.root, text="Login", command=login, width=20)
        login_button.pack(pady=20)
        
        # Bind Enter key to login
        password_entry.bind('<Return>', lambda e: login())
        username_entry.bind('<Return>', lambda e: password_entry.focus())

