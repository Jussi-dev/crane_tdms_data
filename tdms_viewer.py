import os
import pandas as pd
import json
from nptdms import TdmsFile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class TDMSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TDMS Channel Selector & CSV Converter")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Initialize variables
        self.tdms_file = None
        self.channels_data = {}
        self.all_channels = []  # Store all channel display names for filtering
        self.time_column = None
        self.time_column_name = None
        self.settings_file = os.path.join(os.getcwd(), "last_selection.json")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="TDMS File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        ttk.Button(file_frame, text="Browse...", command=self.select_file).grid(row=0, column=2, sticky=tk.E)
        
        # Channel selection section
        channels_frame = ttk.LabelFrame(main_frame, text="Channel Selection", padding="5")
        channels_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        channels_frame.columnconfigure(0, weight=1)
        channels_frame.columnconfigure(2, weight=1)
        channels_frame.rowconfigure(2, weight=1)
        
        # Available channels
        ttk.Label(channels_frame, text="Available Channels").grid(row=0, column=0, pady=(0, 5))
        
        # Search/filter entry
        search_frame = ttk.Frame(channels_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 5))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Filter:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.filter_var = tk.StringVar()
        self.filter_entry = ttk.Entry(search_frame, textvariable=self.filter_var)
        self.filter_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.filter_var.trace('w', self.filter_channels)
        
        clear_button = ttk.Button(search_frame, text="Clear", command=self.clear_filter, width=8)
        clear_button.grid(row=0, column=2, sticky=tk.E)
        
        # Available channels listbox with scrollbar
        available_frame = ttk.Frame(channels_frame)
        available_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 5))
        available_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(0, weight=1)
        
        self.available_listbox = tk.Listbox(available_frame, selectmode=tk.EXTENDED)
        self.available_listbox.grid(row=0, column=0, sticky="nsew")
        
        available_scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=self.available_listbox.yview)
        available_scrollbar.grid(row=0, column=1, sticky="ns")
        self.available_listbox.configure(yscrollcommand=available_scrollbar.set)
        
        # Control buttons
        button_frame = ttk.Frame(channels_frame)
        button_frame.grid(row=2, column=1, padx=10)
        
        ttk.Button(button_frame, text="Add >>", command=self.add_channels).pack(pady=2)
        ttk.Button(button_frame, text="Add All", command=self.add_all_channels).pack(pady=2)
        ttk.Button(button_frame, text="<< Remove", command=self.remove_channels).pack(pady=2)
        ttk.Button(button_frame, text="Remove All", command=self.remove_all_channels).pack(pady=2)
        
        # Selected channels
        ttk.Label(channels_frame, text="Selected Channels").grid(row=0, column=2, pady=(0, 5))
        
        # Selected channels listbox with scrollbar
        selected_frame = ttk.Frame(channels_frame)
        selected_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=(5, 0))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(0, weight=1)
        
        self.selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED)
        self.selected_listbox.grid(row=0, column=0, sticky="nsew")
        
        selected_scrollbar = ttk.Scrollbar(selected_frame, orient="vertical", command=self.selected_listbox.yview)
        selected_scrollbar.grid(row=0, column=1, sticky="ns")
        self.selected_listbox.configure(yscrollcommand=selected_scrollbar.set)
        
        # Export section
        export_frame = ttk.LabelFrame(main_frame, text="Export Options", padding="5")
        export_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        export_frame.columnconfigure(0, weight=1)
        
        # Include time column option
        self.include_time_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, text="Include time/index column", 
                       variable=self.include_time_var).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Export button
        self.export_button = ttk.Button(export_frame, text="Export Selected Channels to CSV", 
                                      command=self.export_to_csv, state=tk.DISABLED)
        self.export_button.grid(row=1, column=0, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Please select a TDMS file")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))



    def select_file(self):
        """Select and load a TDMS file"""
        tdms_path = filedialog.askopenfilename(
            title="Select TDMS File",
            filetypes=[("TDMS files", "*.tdms"), ("All files", "*.*")]
        )
        
        if tdms_path:
            try:
                self.status_var.set("Loading TDMS file...")
                self.update()
                
                # Load the TDMS file
                self.tdms_file = TdmsFile.read(tdms_path)
                self.file_label.config(text=os.path.basename(tdms_path), foreground="black")
                
                # Extract channels and populate the available channels list
                self.load_channels()
                
                self.status_var.set(f"Loaded: {os.path.basename(tdms_path)} - {len(self.channels_data)} channels found")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load TDMS file:\n{str(e)}")
                self.status_var.set("Error loading file")
                
    def load_channels(self):
        """Load channels from the TDMS file and populate the available channels list"""
        if not self.tdms_file:
            return
            
        # Clear previous data
        self.channels_data.clear()
        self.available_listbox.delete(0, tk.END)
        self.selected_listbox.delete(0, tk.END)
        
        # Extract time column (if available)
        self.time_column = None
        self.time_column_name = None
        
        # Collect all channels
        for group in self.tdms_file.groups():
            for channel in group.channels():
                # Handle time column only once
                if self.time_column is None:
                    try:
                        self.time_column = channel.time_track()
                        self.time_column_name = "Time"
                    except (KeyError, AttributeError):
                        # Fallback to index if no time track available
                        if len(channel) > 0:
                            self.time_column = list(range(len(channel)))
                            self.time_column_name = "Index"
                
                # Create unique channel identifier and display name
                channel_id = f"{group.name}/{channel.name}"
                display_name = f"{group.name} - {channel.name}"
                
                # Store channel data
                self.channels_data[channel_id] = {
                    'channel': channel,
                    'display_name': display_name,
                    'data': channel[:]
                }
                
                # Add to available channels list
                self.available_listbox.insert(tk.END, display_name)
                
        # Store all channels for filtering
        self.all_channels = [self.channels_data[channel_id]['display_name'] for channel_id in self.channels_data.keys()]
        
        # Load and apply last selection if available
        self.load_last_selection()
        
        # Enable export button if channels are available
        if self.channels_data:
            self.export_button.config(state=tk.NORMAL)
        
    def add_channels(self):
        """Add selected channels from available to selected list"""
        selection = self.available_listbox.curselection()
        if not selection:
            return
            
        # Get selected items
        selected_items = []
        for index in selection:
            item_text = self.available_listbox.get(index)
            selected_items.append((index, item_text))
        
        # Add to selected list (avoid duplicates)
        for index, item_text in selected_items:
            if item_text not in [self.selected_listbox.get(i) for i in range(self.selected_listbox.size())]:
                self.selected_listbox.insert(tk.END, item_text)
                
        self.update_status()
        
    def add_all_channels(self):
        """Add all available channels to selected list"""
        # Clear selected list first
        self.selected_listbox.delete(0, tk.END)
        
        # Add all available channels
        for i in range(self.available_listbox.size()):
            item_text = self.available_listbox.get(i)
            self.selected_listbox.insert(tk.END, item_text)
            
        self.update_status()
        
    def remove_channels(self):
        """Remove selected channels from selected list"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
            
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.selected_listbox.delete(index)
            
        self.update_status()
        
    def remove_all_channels(self):
        """Remove all channels from selected list"""
        self.selected_listbox.delete(0, tk.END)
        self.update_status()
        
    def update_status(self):
        """Update status bar with current selection info"""
        if not self.channels_data:
            return
            
        selected_count = self.selected_listbox.size()
        total_count = len(self.channels_data)
        visible_count = self.available_listbox.size()
        
        if selected_count == 0:
            if visible_count < total_count:
                self.status_var.set(f"No channels selected (showing {visible_count} of {total_count} available)")
            else:
                self.status_var.set(f"No channels selected ({total_count} available)")
        else:
            if visible_count < total_count:
                self.status_var.set(f"{selected_count} of {total_count} channels selected (showing {visible_count})")
            else:
                self.status_var.set(f"{selected_count} of {total_count} channels selected")
    
    def filter_channels(self, *args):
        """Filter the available channels list based on the search term"""
        if not hasattr(self, 'all_channels') or not self.all_channels:
            return
            
        search_term = self.filter_var.get().lower()
        
        # Clear the listbox
        self.available_listbox.delete(0, tk.END)
        
        # Filter and add matching channels
        for channel_name in self.all_channels:
            if search_term in channel_name.lower():
                self.available_listbox.insert(tk.END, channel_name)
        
        # Update status to show filtered count
        self.update_status()
    
    def clear_filter(self):
        """Clear the filter and show all channels"""
        self.filter_var.set("")
        # The trace will automatically call filter_channels which will show all channels
    
    def export_to_csv(self):
        """Export selected channels to CSV file"""
        if self.selected_listbox.size() == 0:
            messagebox.showwarning("No Selection", "Please select at least one channel to export.")
            return
        
        # Create export directory if it doesn't exist
        export_dir = os.path.join(os.getcwd(), "export")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        # Generate default filename based on TDMS file name
        if hasattr(self, 'tdms_file') and self.file_label.cget('text') != "No file selected":
            base_name = os.path.splitext(self.file_label.cget('text'))[0]
            default_filename = f"{base_name}_export.csv"
        else:
            default_filename = "tdms_export.csv"
        
        # Ask user for filename (with default path in export folder)
        output_file = filedialog.asksaveasfilename(
            title="Save CSV File",
            initialdir=export_dir,
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
            
        try:
            self.status_var.set("Exporting to CSV...")
            self.update()
            
            # Collect selected channels data
            export_data = {}
            
            # Add time/index column if requested
            if self.include_time_var.get() and self.time_column is not None:
                export_data[self.time_column_name] = self.time_column
            
            # Add selected channels
            channel_ids = list(self.channels_data.keys())
            for i in range(self.selected_listbox.size()):
                display_name = self.selected_listbox.get(i)
                
                # Find corresponding channel ID
                for channel_id, channel_info in self.channels_data.items():
                    if channel_info['display_name'] == display_name:
                        # Clean column name for CSV
                        clean_name = display_name.replace("/", "_").replace(" ", "_")
                        clean_name = clean_name.replace(".", "_").replace("-", "_")
                        export_data[clean_name] = channel_info['data']
                        break
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            df.to_csv(output_file, index=False)
            
            # Save current selection for next time
            self.save_last_selection()
            
            messagebox.showinfo("Export Complete", 
                              f"Successfully exported {len(export_data)} columns to:\n{output_file}")
            self.status_var.set(f"Export complete - {len(export_data)} columns saved")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV:\n{str(e)}")
            self.status_var.set("Export failed")
    
    def save_last_selection(self):
        """Save the currently selected channels to a JSON file"""
        try:
            selected_channels = []
            for i in range(self.selected_listbox.size()):
                selected_channels.append(self.selected_listbox.get(i))
            
            settings = {
                "last_selected_channels": selected_channels,
                "include_time_column": self.include_time_var.get()
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save selection: {e}")
    
    def load_last_selection(self):
        """Load and apply the last selected channels from JSON file"""
        try:
            if not os.path.exists(self.settings_file):
                return
                
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            
            last_channels = settings.get("last_selected_channels", [])
            include_time = settings.get("include_time_column", True)
            
            # Apply time column setting
            self.include_time_var.set(include_time)
            
            # Apply channel selection
            for channel_name in last_channels:
                # Check if this channel exists in current file
                for i in range(self.available_listbox.size()):
                    if self.available_listbox.get(i) == channel_name:
                        # Add to selected list if not already there
                        if channel_name not in [self.selected_listbox.get(j) for j in range(self.selected_listbox.size())]:
                            self.selected_listbox.insert(tk.END, channel_name)
                        break
            
            self.update_status()
            
            if last_channels:
                restored_count = self.selected_listbox.size()
                self.status_var.set(f"Restored {restored_count} previously selected channels")
                
        except Exception as e:
            print(f"Warning: Could not load last selection: {e}")



if __name__ == "__main__":
    viewer = TDMSViewer()
    viewer.mainloop()