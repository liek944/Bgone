"""GUI entry point for Bgone - Background Remover."""

import threading
from pathlib import Path
from tkinter import filedialog
from typing import Optional

import customtkinter as ctk
from PIL import Image

from app.config import OUTPUT_DIR, DEFAULT_SUFFIX, SUPPORTED_FORMATS
from app.processor import process_image
from app.batch import process_folder, get_output_path, BatchResult


class CancelledException(Exception):
    """Raised when processing is cancelled by user."""


class BgoneApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Bgone - Background Remover")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State
        self.selected_file: Optional[Path] = None
        self.selected_folder: Optional[Path] = None
        self.output_dir: Path = OUTPUT_DIR.resolve()
        self.suffix: str = DEFAULT_SUFFIX
        self.overwrite: bool = False
        self.processing: bool = False
        self.cancel_event: threading.Event = threading.Event()
        
        # Build UI
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        title = ctk.CTkLabel(
            header, 
            text="Bgone", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Remove backgrounds instantly",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle.pack(side="left", padx=15)
        
        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.tab_single = self.tabview.add("Single File")
        self.tab_batch = self.tabview.add("Batch Folder")
        self.tab_settings = self.tabview.add("Settings")
        
        self._create_single_tab()
        self._create_batch_tab()
        self._create_settings_tab()
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.progress = ctk.CTkProgressBar(self.status_frame)
        self.progress.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.progress.set(0)
    
    def _create_single_tab(self):
        """Create single file processing tab."""
        tab = self.tab_single
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # File selection frame
        select_frame = ctk.CTkFrame(tab)
        select_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        select_frame.grid_columnconfigure(1, weight=1)
        
        self.file_label = ctk.CTkLabel(
            select_frame,
            text="No file selected",
            anchor="w"
        )
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        select_btn = ctk.CTkButton(
            select_frame,
            text="Select Image",
            command=self._select_file,
            width=120
        )
        select_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Preview area (placeholder)
        preview_frame = ctk.CTkFrame(tab)
        preview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="Drop an image here or use the button above\n\nSupported formats: JPG, PNG, WEBP",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.preview_label.grid(row=0, column=0, padx=20, pady=40)
        
        # Button frame for process/cancel buttons
        single_btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        single_btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        single_btn_frame.grid_columnconfigure(0, weight=1)
        
        # Process button
        self.process_single_btn = ctk.CTkButton(
            single_btn_frame,
            text="Remove Background",
            command=self._process_single,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.process_single_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Cancel button (hidden initially)
        self.cancel_single_btn = ctk.CTkButton(
            single_btn_frame,
            text="Cancel",
            command=self._cancel_processing,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        # Cancel button not shown initially
    
    def _create_batch_tab(self):
        """Create batch folder processing tab."""
        tab = self.tab_batch
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Folder selection frame
        select_frame = ctk.CTkFrame(tab)
        select_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        select_frame.grid_columnconfigure(1, weight=1)
        
        self.folder_label = ctk.CTkLabel(
            select_frame,
            text="No folder selected",
            anchor="w"
        )
        self.folder_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        select_btn = ctk.CTkButton(
            select_frame,
            text="Select Folder",
            command=self._select_folder,
            width=120
        )
        select_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Log area
        log_frame = ctk.CTkFrame(tab)
        log_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = ctk.CTkTextbox(log_frame, state="disabled")
        self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Button frame for process/cancel buttons
        batch_btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        batch_btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        batch_btn_frame.grid_columnconfigure(0, weight=1)
        
        # Process button
        self.process_batch_btn = ctk.CTkButton(
            batch_btn_frame,
            text="Process All Images",
            command=self._process_batch,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.process_batch_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Cancel button (hidden initially)
        self.cancel_batch_btn = ctk.CTkButton(
            batch_btn_frame,
            text="Cancel",
            command=self._cancel_processing,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        # Cancel button not shown initially
    
    def _create_settings_tab(self):
        """Create settings tab."""
        tab = self.tab_settings
        tab.grid_columnconfigure(1, weight=1)
        
        # Output directory
        ctk.CTkLabel(tab, text="Output Directory:").grid(
            row=0, column=0, padx=10, pady=15, sticky="w"
        )
        
        output_frame = ctk.CTkFrame(tab, fg_color="transparent")
        output_frame.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_entry = ctk.CTkEntry(output_frame)
        self.output_entry.grid(row=0, column=0, sticky="ew")
        self.output_entry.insert(0, str(self.output_dir))
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="Browse",
            command=self._browse_output,
            width=80
        )
        browse_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Suffix
        ctk.CTkLabel(tab, text="Filename Suffix:").grid(
            row=1, column=0, padx=10, pady=15, sticky="w"
        )
        
        self.suffix_entry = ctk.CTkEntry(tab, width=200)
        self.suffix_entry.grid(row=1, column=1, padx=10, pady=15, sticky="w")
        self.suffix_entry.insert(0, self.suffix)
        
        # Overwrite
        ctk.CTkLabel(tab, text="Overwrite Existing:").grid(
            row=2, column=0, padx=10, pady=15, sticky="w"
        )
        
        self.overwrite_switch = ctk.CTkSwitch(
            tab,
            text="",
            command=self._toggle_overwrite
        )
        self.overwrite_switch.grid(row=2, column=1, padx=10, pady=15, sticky="w")
        
        # Info
        info_label = ctk.CTkLabel(
            tab,
            text="Settings are applied to the next processing operation.",
            text_color="gray"
        )
        info_label.grid(row=3, column=0, columnspan=2, padx=10, pady=30, sticky="w")
    
    def _select_file(self):
        """Open file dialog to select an image."""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.webp"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=filetypes
        )
        if filename:
            self.selected_file = Path(filename)
            self.file_label.configure(text=self.selected_file.name)
            self.process_single_btn.configure(state="normal")
            self._set_status(f"Selected: {self.selected_file.name}")
    
    def _select_folder(self):
        """Open folder dialog to select input folder."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.selected_folder = Path(folder)
            # Count valid files
            count = sum(
                1 for f in self.selected_folder.iterdir()
                if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
            )
            self.folder_label.configure(
                text=f"{self.selected_folder.name} ({count} images)"
            )
            self.process_batch_btn.configure(state="normal" if count > 0 else "disabled")
            self._set_status(f"Selected folder with {count} images")
    
    def _browse_output(self):
        """Browse for output directory."""
        folder = filedialog.askdirectory(title="Select Output Directory")
        if folder:
            self.output_dir = Path(folder)
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, str(self.output_dir))
    
    def _toggle_overwrite(self):
        """Toggle overwrite setting."""
        self.overwrite = self.overwrite_switch.get() == 1
    
    def _get_current_settings(self) -> tuple[Path, str, bool]:
        """Get current settings from UI."""
        output_dir = Path(self.output_entry.get())
        suffix = self.suffix_entry.get()
        overwrite = self.overwrite_switch.get() == 1
        return output_dir, suffix, overwrite
    
    def _set_status(self, message: str):
        """Update status bar."""
        self.status_label.configure(text=message)
    
    def _log(self, message: str):
        """Append message to batch log."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def _cancel_processing(self):
        """Signal cancellation of current processing."""
        if self.processing:
            self.cancel_event.set()
            self._set_status("Cancelling...")
            self._log("Cancellation requested...")
    
    def _show_cancel_button(self, show: bool, is_batch: bool = True):
        """Show or hide the cancel button."""
        if is_batch:
            if show:
                self.cancel_batch_btn.grid(row=0, column=1, padx=(5, 0), sticky="e")
            else:
                self.cancel_batch_btn.grid_forget()
        else:
            if show:
                self.cancel_single_btn.grid(row=0, column=1, padx=(5, 0), sticky="e")
            else:
                self.cancel_single_btn.grid_forget()
    
    def _process_single(self):
        """Process single file in background thread."""
        if not self.selected_file or self.processing:
            return
        
        output_dir, suffix, overwrite = self._get_current_settings()
        output_path = get_output_path(self.selected_file, output_dir, suffix)
        
        # Check existing
        if output_path.exists() and not overwrite:
            self._set_status(f"Skipped: {output_path.name} already exists")
            return
        
        self.processing = True
        self.cancel_event.clear()
        self.process_single_btn.configure(state="disabled")
        self._show_cancel_button(True, is_batch=False)
        self.progress.set(0)
        self._set_status(f"Processing: {self.selected_file.name}...")
        
        def process():
            try:
                # Note: Single image processing is atomic and cannot be interrupted mid-operation
                # The cancel button will prevent subsequent operations if in batch mode
                process_image(self.selected_file, output_path)
                if self.cancel_event.is_set():
                    # If cancelled, delete the output file if it was created
                    if output_path.exists():
                        output_path.unlink()
                    self.after(0, lambda: self._on_single_complete(False, "Cancelled"))
                else:
                    self.after(0, lambda: self._on_single_complete(True, output_path))
            except Exception as e:
                self.after(0, lambda: self._on_single_complete(False, str(e)))
        
        threading.Thread(target=process, daemon=True).start()
    
    def _on_single_complete(self, success: bool, result):
        """Handle single file processing completion."""
        self.processing = False
        self.cancel_event.clear()
        self.process_single_btn.configure(state="normal")
        self._show_cancel_button(False, is_batch=False)
        self.progress.set(1 if success else 0)
        
        if success:
            self._set_status(f"✓ Saved: {result}")
        elif result == "Cancelled":
            self._set_status("⊘ Processing cancelled")
        else:
            self._set_status(f"✗ Error: {result}")
    
    def _process_batch(self):
        """Process folder in background thread."""
        if not self.selected_folder or self.processing:
            return
        
        output_dir, suffix, overwrite = self._get_current_settings()
        
        self.processing = True
        self.cancel_event.clear()
        self.process_batch_btn.configure(state="disabled")
        self._show_cancel_button(True, is_batch=True)
        self.progress.set(0)
        self._log(f"\n--- Starting batch: {self.selected_folder} ---")
        self._set_status("Processing...")
        
        def process():
            try:
                # Get file count for progress
                files = [
                    f for f in self.selected_folder.iterdir()
                    if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
                ]
                total = len(files)
                
                # Process each file manually for progress updates
                processed = 0
                skipped = 0
                failed = 0
                
                for i, input_file in enumerate(files):
                    # Check for cancellation before processing each file
                    if self.cancel_event.is_set():
                        self.after(0, lambda: self._log("--- Batch cancelled by user ---"))
                        result = BatchResult(processed, skipped, failed, [], cancelled=True)
                        self.after(0, lambda r=result: self._on_batch_complete(r))
                        return
                    
                    out_path = get_output_path(input_file, output_dir, suffix)
                    
                    if out_path.exists() and not overwrite:
                        skipped += 1
                        self.after(0, lambda f=input_file: self._log(f"Skipped: {f.name}"))
                    else:
                        try:
                            process_image(input_file, out_path)
                            processed += 1
                            self.after(0, lambda f=input_file: self._log(f"✓ {f.name}"))
                        except Exception as e:
                            failed += 1
                            self.after(0, lambda f=input_file, e=e: self._log(f"✗ {f.name}: {e}"))
                    
                    # Update progress
                    progress = (i + 1) / total
                    self.after(0, lambda p=progress: self.progress.set(p))
                
                result = BatchResult(processed, skipped, failed, [])
                self.after(0, lambda: self._on_batch_complete(result))
                
            except Exception as e:
                self.after(0, lambda: self._on_batch_error(str(e)))
        
        threading.Thread(target=process, daemon=True).start()
    
    def _on_batch_complete(self, result: BatchResult):
        """Handle batch processing completion."""
        self.processing = False
        self.cancel_event.clear()
        self.process_batch_btn.configure(state="normal")
        self._show_cancel_button(False, is_batch=True)
        
        if getattr(result, 'cancelled', False):
            msg = f"Cancelled: {result.processed} processed, {result.skipped} skipped, {result.failed} failed"
            self._set_status("⊘ Batch processing cancelled")
        else:
            msg = f"Done: {result.processed} processed, {result.skipped} skipped, {result.failed} failed"
            self._set_status(msg)
        self._log(msg)
    
    def _on_batch_error(self, error: str):
        """Handle batch processing error."""
        self.processing = False
        self.cancel_event.clear()
        self.process_batch_btn.configure(state="normal")
        self._show_cancel_button(False, is_batch=True)
        self._set_status(f"Error: {error}")
        self._log(f"Error: {error}")


def main():
    """Launch the GUI application."""
    app = BgoneApp()
    app.mainloop()


if __name__ == "__main__":
    main()
