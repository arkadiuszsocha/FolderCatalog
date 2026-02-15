"""
GUI module for Folder Catalog application.
Contains all UI components and user interaction logic.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable, Dict, List
from pathlib import Path
import threading
import time

from database import ScannedFolder, DatabaseManager, FolderItem
from scanner import FolderScanner


class LabelDialog:
    """Dialog for entering a folder label."""
    
    def __init__(self, parent: tk.Tk, default_label: str = ""):
        """
        Initialize label dialog.
        
        Args:
            parent: Parent window
            default_label: Default text for the label input
        """
        self.result: Optional[str] = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enter Label")
        self.dialog.geometry("400x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets(default_label)
        self._center_window(parent)
    
    def _create_widgets(self, default_label: str) -> None:
        """Create dialog widgets."""
        # Label
        ttk.Label(
            self.dialog, 
            text="Enter a label for this folder:"
        ).pack(pady=10, padx=20)
        
        # Entry
        self.entry = ttk.Entry(self.dialog, width=40)
        self.entry.pack(pady=5, padx=20)
        self.entry.insert(0, default_label)
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame, 
            text="OK", 
            command=self._on_ok,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self._on_cancel,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Bindings
        self.entry.bind('<Return>', lambda e: self._on_ok())
        self.entry.bind('<Escape>', lambda e: self._on_cancel())
    
    def _center_window(self, parent: tk.Tk) -> None:
        """Center dialog on parent window."""
        self.dialog.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _on_ok(self) -> None:
        """Handle OK button click."""
        self.result = self.entry.get().strip()
        self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[str]:
        """
        Show dialog and wait for result.
        
        Returns:
            Entered label or None if cancelled
        """
        self.dialog.wait_window()
        return self.result


class FolderListPanel(ttk.LabelFrame):
    """Left panel showing list of scanned folders."""
    
    def __init__(self, parent: tk.Widget, on_select: Callable[[Optional[int]], None]):
        """
        Initialize folder list panel.
        
        Args:
            parent: Parent widget
            on_select: Callback when folder is selected (receives folder_id)
        """
        super().__init__(parent, text="Scanned Folders", padding="5")
        self.on_select = on_select
        self.folder_ids: list[int] = []
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create panel widgets."""
        # Listbox with scrollbar
        scroll_frame = ttk.Frame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(
            scroll_frame,
            width=35,
            yscrollcommand=scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind('<<ListboxSelect>>', self._on_selection_change)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.add_button = ttk.Button(
            button_frame, 
            text="Add Folder",
            width=12
        )
        self.add_button.pack(side=tk.LEFT, padx=2)
        
        self.remove_button = ttk.Button(
            button_frame, 
            text="Remove",
            width=10
        )
        self.remove_button.pack(side=tk.LEFT, padx=2)
        
        self.scan_button = ttk.Button(
            button_frame, 
            text="Scan/Update",
            width=12
        )
        self.scan_button.pack(side=tk.LEFT, padx=2)
    
    def _on_selection_change(self, event) -> None:
        """Handle listbox selection change."""
        selection = self.listbox.curselection()
        if selection:
            folder_id = self.folder_ids[selection[0]]
            self.on_select(folder_id)
        else:
            self.on_select(None)
    
    def load_folders(self, folders: list[ScannedFolder]) -> None:
        """
        Load folders into the listbox.
        
        Args:
            folders: List of ScannedFolder objects
        """
        self.listbox.delete(0, tk.END)
        self.folder_ids.clear()
        
        for folder in folders:
            self.folder_ids.append(folder.id)
            display_text = f"{folder.label}"
            
            if folder.last_scan:
                display_text += f" [{folder.file_count} files, {folder.folder_count} folders]"
            
            self.listbox.insert(tk.END, display_text)
    
    def get_selected_folder_id(self) -> Optional[int]:
        """
        Get ID of currently selected folder.
        
        Returns:
            Folder ID or None if no selection
        """
        selection = self.listbox.curselection()
        if selection:
            return self.folder_ids[selection[0]]
        return None
    
    def remove_selected(self) -> None:
        """Remove currently selected item from list."""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)
            del self.folder_ids[index]


class FolderTreePanel(ttk.LabelFrame):
    """Right panel showing folder tree structure."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize folder tree panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, text="Folder Contents", padding="5")
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create panel widgets."""
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Treeview
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.tree.yview)
        
        # Configure columns
        self.tree['columns'] = ('type', 'size')
        self.tree.column('#0', width=400, minwidth=200)
        self.tree.column('type', width=100, minwidth=50)
        self.tree.column('size', width=100, minwidth=50)
        
        self.tree.heading('#0', text='Name', anchor=tk.W)
        self.tree.heading('type', text='Type', anchor=tk.W)
        self.tree.heading('size', text='Size', anchor=tk.W)
        
        # Grid configuration
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._batch_load_id = 0
        self._batch_continue = True
    
    def clear(self) -> None:
        """Clear all items from the tree."""
        self.tree.delete(*self.tree.get_children())

    def clear_batched(self, root: tk.Tk, batch_size: int = 500, done: Optional[Callable[[], None]] = None) -> None:
        """Clear tree in batches so UI stays responsive when tree is huge."""
        children = list(self.tree.get_children())
        if not children:
            if done:
                done()
            return
        n = len(children)
        idx = [0]

        def delete_batch() -> None:
            end = min(idx[0] + batch_size, n)
            self.tree.delete(*children[idx[0]:end])
            idx[0] = end
            if idx[0] < n:
                root.after(5, delete_batch)
            elif done:
                done()
        delete_batch()
    
    def load_contents_batched(
        self,
        root: tk.Tk,
        items: List[FolderItem],
        format_size: Callable[[int], str],
        load_id: int,
        batch_size: int = 800,
        status_callback: Optional[Callable[[str], None]] = None,
        done_callback: Optional[Callable[[int], None]] = None,
    ) -> None:
        """Load folder contents into tree in batches so the UI stays responsive."""
        self._batch_continue = True
        self._batch_load_id = load_id
        self.clear()
        if not items:
            if done_callback:
                done_callback(0)
            return
        tree_items: Dict[str, str] = {}
        total = len(items)
        idx = [0]  # use list so closure can mutate

        def process_batch() -> None:
            if not self._batch_continue or load_id != self._batch_load_id:
                return
            end = min(idx[0] + batch_size, total)
            for i in range(idx[0], end):
                if not self._batch_continue or load_id != self._batch_load_id:
                    return
                item = items[i]
                parts = Path(item.path).parts
                parent_path = str(Path(*parts[:-1])) if len(parts) > 1 else ''
                parent_id = tree_items.get(parent_path, '')
                item_type = "Folder" if item.is_directory else "File"
                size_str = format_size(item.size) if not item.is_directory else ""
                item_id = self.tree.insert(
                    parent_id, tk.END, text=item.name,
                    values=(item_type, size_str), open=False
                )
                tree_items[item.path] = item_id
            idx[0] = end
            if status_callback:
                status_callback(f"Loading... {end:,} of {total:,} items")
            if idx[0] < total:
                root.after(5, process_batch)
            else:
                if done_callback:
                    done_callback(total)
        process_batch()

    def load_contents(self, items: list, format_size: Callable[[int], str]) -> None:
        """
        Load folder contents into tree view.
        
        Args:
            items: List of FolderItem objects
            format_size: Function to format file sizes
        """
        self.clear()
        
        if not items:
            return
        
        # Build tree structure
        tree_items: Dict[str, str] = {}  # path -> tree_item_id
        
        for item in items:
            parts = Path(item.path).parts
            parent_path = str(Path(*parts[:-1])) if len(parts) > 1 else ''
            parent_id = tree_items.get(parent_path, '')
            
            item_type = "Folder" if item.is_directory else "File"
            size_str = format_size(item.size) if not item.is_directory else ""
            
            item_id = self.tree.insert(
                parent_id,
                tk.END,
                text=item.name,
                values=(item_type, size_str),
                open=False
            )
            
            tree_items[item.path] = item_id


class StatusBar(ttk.Label):
    """Status bar for displaying application messages."""
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize status bar.
        
        Args:
            parent: Parent widget
        """
        self.text_var = tk.StringVar(value="Ready")
        super().__init__(
            parent, 
            textvariable=self.text_var, 
            relief=tk.SUNKEN,
            padding=(5, 2)
        )
    
    def set_message(self, message: str) -> None:
        """
        Set status bar message.
        
        Args:
            message: Message to display
        """
        self.text_var.set(message)
    
    def clear(self) -> None:
        """Clear status bar message."""
        self.text_var.set("Ready")


class FolderScannerGUI:
    """Main GUI controller for Folder Catalog application."""
    
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        """
        Initialize GUI.
        
        Args:
            root: Root Tk window
            db_manager: Database manager instance
        """
        self.root = root
        self.db_manager = db_manager
        self.scanner = FolderScanner()
        self._folder_load_id = 0
        
        self._configure_window()
        self._create_widgets()
        # Bring window to front once it's shown (avoids having to click menu bar on macOS)
        self.root.after(150, self._bring_window_to_front)
        # Load folder list in background so window appears and stays responsive
        self.status_bar.set_message("Loading...")
        self.root.after(0, self._start_initial_load)
    
    def _bring_window_to_front(self) -> None:
        """Raise and focus the window so it appears in front when app starts."""
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(50, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def _start_initial_load(self) -> None:
        """Start loading folders from DB in a background thread."""
        def fetch() -> None:
            try:
                folders = self.db_manager.get_all_folders()
                self.root.after(0, lambda: self._apply_initial_folders(folders, None))
            except Exception as e:
                self.root.after(0, lambda: self._apply_initial_folders([], e))
        threading.Thread(target=fetch, daemon=True).start()
    
    def _apply_initial_folders(self, folders: list, error: Optional[BaseException]) -> None:
        """Apply loaded folders to UI (called on main thread)."""
        if error is not None:
            messagebox.showerror("Error", f"Failed to load folders: {str(error)}")
        else:
            self.folder_list.load_folders(folders)
        self.status_bar.set_message("Ready")
    
    def _configure_window(self) -> None:
        """Configure main window."""
        self.root.title("Folder Catalog")
        self.root.geometry("1100x650")
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - defer selection handler so listbox click returns immediately (avoids freeze)
        self.folder_list = FolderListPanel(
            main_frame,
            on_select=lambda folder_id: self.root.after(0, lambda f=folder_id: self._on_folder_selected(f)),
        )
        self.folder_list.grid(
            row=0, column=0, 
            sticky=(tk.W, tk.E, tk.N, tk.S), 
            padx=(0, 5)
        )
        
        # Connect buttons
        self.folder_list.add_button.config(command=self._add_folder)
        self.folder_list.remove_button.config(command=self._remove_folder)
        self.folder_list.scan_button.config(command=self._scan_folder)
        
        # Right panel
        self.tree_panel = FolderTreePanel(main_frame)
        self.tree_panel.grid(
            row=0, column=1, 
            sticky=(tk.W, tk.E, tk.N, tk.S)
        )
        
        # Status area: message + progress bar (progress bar shown only during scan)
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(
            row=1, column=0, columnspan=2,
            sticky=(tk.W, tk.E),
            pady=(5, 0)
        )
        status_frame.columnconfigure(0, weight=1)
        self.status_bar = StatusBar(status_frame)
        self.status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.scan_progress = ttk.Progressbar(
            status_frame, mode='indeterminate', length=300
        )
        self.scan_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
        self.scan_progress.grid_remove()  # hidden until scan starts
    
    def _add_folder(self) -> None:
        """Handle add folder button click."""
        folder_path = filedialog.askdirectory(title="Select Folder to Scan")
        if not folder_path:
            return
        
        # Get label from user
        default_label = Path(folder_path).name
        dialog = LabelDialog(self.root, default_label)
        label = dialog.show()
        
        if not label:
            return
        
        try:
            # Add to database
            self.db_manager.add_folder(label, folder_path)
            
            # Reload list
            folders = self.db_manager.get_all_folders()
            self.folder_list.load_folders(folders)
            
            self.status_bar.set_message(f"Added folder: {label}")
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Error", "This folder is already in the list!")
            else:
                messagebox.showerror("Error", f"Failed to add folder: {str(e)}")
    
    def _remove_folder(self) -> None:
        """Handle remove folder button click."""
        folder_id = self.folder_list.get_selected_folder_id()
        if folder_id is None:
            messagebox.showwarning("Warning", "Please select a folder to remove")
            return
        
        if not messagebox.askyesno("Confirm", "Remove this folder from the list?"):
            return
        
        try:
            self.db_manager.remove_folder(folder_id)
            self.folder_list.remove_selected()
            self.tree_panel.clear()
            self.status_bar.set_message("Folder removed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove folder: {str(e)}")
    
    def _scan_folder(self) -> None:
        """Handle scan folder button click. Runs scan in background with progress bar."""
        folder_id = self.folder_list.get_selected_folder_id()
        if folder_id is None:
            messagebox.showwarning("Warning", "Please select a folder to scan")
            return
        
        folder = self.db_manager.get_folder_by_id(folder_id)
        if folder is None:
            messagebox.showerror("Error", "Folder not found in database")
            return
        
        if not self.scanner.validate_path(folder.path):
            messagebox.showerror("Error", "Folder no longer exists or is not accessible!")
            return
        
        # Show progress bar and disable scan button during scan
        self.scan_progress.grid()
        self.scan_progress.start(8)
        self.folder_list.scan_button.config(state=tk.DISABLED)
        self.status_bar.set_message(f"Scanning {folder.label}...")
        
        def do_scan() -> None:
            result: List = [None, None, None]  # items, file_count, folder_count
            error: List = [None]  # exception
            last_update = [0.0]  # throttle progress updates
            pending_message = [None]  # str or None
            def progress(path: str) -> None:
                now = time.monotonic()
                if now - last_update[0] < 0.2:  # at most every 200ms
                    pending_message[0] = path
                    return
                last_update[0] = now
                msg = path
                if len(msg) > 60:
                    msg = "..." + msg[-57:]
                self.root.after(0, lambda: self.status_bar.set_message(f"Scanning: {msg}"))
            try:
                items, fc, fd = self.scanner.scan_directory(
                    folder.path, progress_callback=progress
                )
                result[0], result[1], result[2] = items, fc, fd
            except Exception as e:
                error[0] = e
            # Do DB write in background thread so main thread stays responsive
            if error[0] is None:
                items, file_count, folder_count = result[0], result[1], result[2]
                try:
                    self.db_manager.update_folder_scan(
                        folder_id, items, file_count, folder_count
                    )
                except Exception as e:
                    error[0] = e
            
            def on_done() -> None:
                self.scan_progress.stop()
                self.scan_progress.grid_remove()
                self.folder_list.scan_button.config(state=tk.NORMAL)
                if error[0] is not None:
                    e = error[0]
                    if isinstance(e, PermissionError):
                        messagebox.showerror("Permission Denied", str(e))
                        self.status_bar.set_message("Scan failed: Permission denied")
                    else:
                        messagebox.showerror("Error", f"Failed to scan folder: {str(e)}")
                        self.status_bar.set_message("Scan failed")
                    return
                items, file_count, folder_count = result[0], result[1], result[2]
                # Only UI updates on main thread; DB was already updated in thread
                if len(items) > 2000:
                    self._folder_load_id += 1
                    self.tree_panel.load_contents_batched(
                        self.root, items, self.scanner.format_size,
                        self._folder_load_id, batch_size=800,
                        status_callback=self.status_bar.set_message,
                        done_callback=lambda n: self._scan_done(folder_count, file_count),
                    )
                else:
                    self.tree_panel.load_contents(items, self.scanner.format_size)
                    self._scan_done(folder_count, file_count)
            
            self.root.after(0, on_done)
        
        def _scan_done(folder_count: int, file_count: int) -> None:
            folders = self.db_manager.get_all_folders()
            self.folder_list.load_folders(folders)
            self.status_bar.set_message(
                f"Scan complete: {folder_count} folders, {file_count} files"
            )
        
        self._scan_done = _scan_done
        threading.Thread(target=do_scan, daemon=True).start()
    
    def _on_folder_selected(self, folder_id: Optional[int]) -> None:
        """
        Handle folder selection in left panel.
        Loads contents in a background thread and fills the tree in batches to keep UI responsive.
        """
        if folder_id is None:
            self.tree_panel._batch_continue = False
            self.tree_panel.clear()
            return
        
        self._folder_load_id += 1
        load_id = self._folder_load_id
        self.tree_panel._batch_continue = False  # cancel any previous load
        self.tree_panel.clear()
        self.status_bar.set_message("Loading...")
        
        def fetch_then_load() -> None:
            try:
                items = self.db_manager.get_folder_contents(folder_id)
                def on_main() -> None:
                    if load_id != self._folder_load_id:
                        return
                    if not items:
                        self.tree_panel.clear()
                        self.status_bar.set_message("No data - click 'Scan/Update' to scan this folder")
                    else:
                        self.tree_panel.load_contents_batched(
                            self.root,
                            items,
                            self.scanner.format_size,
                            load_id,
                            batch_size=800,
                            status_callback=self.status_bar.set_message,
                            done_callback=lambda n: self.status_bar.set_message(f"Showing {n:,} items"),
                        )
                self.root.after(0, on_main)
            except Exception as e:
                def show_err() -> None:
                    if load_id == self._folder_load_id:
                        messagebox.showerror("Error", f"Failed to load folder: {str(e)}")
                        self.status_bar.set_message("Load failed")
                self.root.after(0, show_err)
        
        threading.Thread(target=fetch_then_load, daemon=True).start()
