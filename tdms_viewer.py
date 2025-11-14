import os
import pandas as pd
import json
from datetime import datetime, timedelta
from nptdms import TdmsFile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class TDMSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TDMS Channel Selector & CSV Converter v1.1.0")
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Initialize variables
        self.tdms_files = []  # List to store multiple TDMS files
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
        
        # File selection buttons
        button_subframe = ttk.Frame(file_frame)
        button_subframe.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        
        ttk.Button(button_subframe, text="Add TDMS Files...", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_subframe, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        
        # Files list with scrollbar
        files_list_frame = ttk.Frame(file_frame)
        files_list_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 5))
        files_list_frame.columnconfigure(0, weight=1)
        
        ttk.Label(files_list_frame, text="Selected Files:").grid(row=0, column=0, sticky=tk.W, pady=(0, 2))
        
        list_container = ttk.Frame(files_list_frame)
        list_container.grid(row=1, column=0, sticky="ew")
        list_container.columnconfigure(0, weight=1)
        
        self.files_listbox = tk.Listbox(list_container, height=4, selectmode=tk.EXTENDED)
        self.files_listbox.grid(row=0, column=0, sticky="ew")
        
        files_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.grid(row=0, column=1, sticky="ns")
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        # Remove selected files button
        ttk.Button(files_list_frame, text="Remove Selected", command=self.remove_selected_files).grid(row=2, column=0, sticky=tk.W, pady=(2, 0))
        
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
        
        # Calculated timestamp column option
        self.include_timestamp_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="Create calculated timestamp column (from MachineStatus - Timestamp)", 
                       variable=self.include_timestamp_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Include group names in column headers option
        self.include_group_names_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, text="Include group names in column headers (e.g., 'Group_ChannelName' vs 'ChannelName')", 
                       variable=self.include_group_names_var).grid(row=2, column=0, sticky=tk.W, pady=2)
        
        # Export button
        self.export_button = ttk.Button(export_frame, text="Export Selected Channels to CSV", 
                                      command=self.export_to_csv, state=tk.DISABLED)
        self.export_button.grid(row=3, column=0, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Please select a TDMS file")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))



    def add_files(self):
        """Add TDMS files to the processing list"""
        # Get the last used directory or default to current working directory
        initial_dir = self.get_last_import_directory()
        
        file_paths = filedialog.askopenfilenames(
            title="Select TDMS Files",
            initialdir=initial_dir,
            filetypes=[("TDMS files", "*.tdms"), ("All files", "*.*")]
        )
        
        if file_paths:
            try:
                self.status_var.set("Loading TDMS files...")
                self.update()
                
                # Add new files to the list (avoid duplicates)
                added_count = 0
                for file_path in file_paths:
                    if file_path not in [f['path'] for f in self.tdms_files]:
                        # Load and validate the TDMS file
                        tdms_file = TdmsFile.read(file_path)
                        
                        self.tdms_files.append({
                            'path': file_path,
                            'name': os.path.basename(file_path),
                            'tdms_obj': tdms_file
                        })
                        
                        # Add to listbox
                        self.files_listbox.insert(tk.END, os.path.basename(file_path))
                        added_count += 1
                
                # Save the directory for next time
                if file_paths:
                    self.save_last_import_directory(os.path.dirname(file_paths[0]))
                
                # Reload channels from all files
                self.load_channels()
                
                if added_count > 0:
                    self.status_var.set(f"Added {added_count} files. Total: {len(self.tdms_files)} files, {len(self.channels_data)} channels found")
                else:
                    self.status_var.set(f"No new files added. Total: {len(self.tdms_files)} files")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load TDMS files:\n{str(e)}")
                self.status_var.set("Error loading files")
    
    def clear_files(self):
        """Clear all selected files"""
        self.tdms_files.clear()
        self.files_listbox.delete(0, tk.END)
        
        # Clear channels data
        self.channels_data.clear()
        self.available_listbox.delete(0, tk.END)
        self.selected_listbox.delete(0, tk.END)
        self.all_channels.clear()
        
        # Disable export button
        self.export_button.config(state=tk.DISABLED)
        
        self.status_var.set("All files cleared")
    
    def remove_selected_files(self):
        """Remove selected files from the list"""
        selection = self.files_listbox.curselection()
        if not selection:
            return
        
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.files_listbox.delete(index)
            if index < len(self.tdms_files):
                self.tdms_files.pop(index)
        
        # Reload channels from remaining files
        if self.tdms_files:
            self.load_channels()
            self.status_var.set(f"Files removed. Remaining: {len(self.tdms_files)} files, {len(self.channels_data)} channels")
        else:
            self.clear_files()
                
    def load_channels(self):
        """Load channels from all TDMS files and populate the available channels list"""
        if not self.tdms_files:
            return
            
        # Clear previous data
        self.channels_data.clear()
        self.available_listbox.delete(0, tk.END)
        self.selected_listbox.delete(0, tk.END)
        
        # Sort files by name (assuming chronological naming)
        sorted_files = sorted(self.tdms_files, key=lambda x: x['name'])
        
        # Extract time column (if available) and concatenate data from all files
        self.time_column = None
        self.time_column_name = None
        
        # Dictionary to collect data from all files for each channel
        combined_channels = {}
        
        # Process all files in chronological order
        for file_info in sorted_files:
            tdms_file = file_info['tdms_obj']
            file_name = file_info['name']
            
            # Collect all channels from this file
            for group in tdms_file.groups():
                for channel in group.channels():
                    # Handle time column - concatenate from all files (do this once per file)
                    if channel == list(group.channels())[0]:  # First channel of each group
                        try:
                            time_data = channel.time_track()
                            if self.time_column is None:
                                self.time_column = list(time_data)
                                self.time_column_name = "Time"
                            else:
                                # Append time data from this file
                                self.time_column.extend(time_data)
                        except (KeyError, AttributeError):
                            # Fallback to index if no time track available
                            if self.time_column is None and len(channel) > 0:
                                self.time_column = list(range(len(channel)))
                                self.time_column_name = "Index"
                            elif self.time_column is not None and len(channel) > 0:
                                # Extend index for additional data
                                start_idx = len(self.time_column)
                                self.time_column.extend(range(start_idx, start_idx + len(channel)))
                    
                    # Create channel identifier (without file name since we're combining)
                    channel_id = f"{group.name}/{channel.name}"
                    display_name = f"{group.name} - {channel.name}"
                    
                    # Collect data from this file
                    if channel_id not in combined_channels:
                        combined_channels[channel_id] = {
                            'display_name': display_name,
                            'data': list(channel[:]),
                            'group_name': group.name,
                            'channel_name': channel.name,
                            'files_count': 1
                        }
                    else:
                        # Append data from this file to existing channel
                        combined_channels[channel_id]['data'].extend(channel[:])
                        combined_channels[channel_id]['files_count'] += 1
        
        # Store the combined channel data
        self.channels_data = combined_channels
        
        # Add channels to available list (sorted by display name)
        sorted_channels = sorted(combined_channels.items(), key=lambda x: x[1]['display_name'])
        for channel_id, channel_info in sorted_channels:
            self.available_listbox.insert(tk.END, channel_info['display_name'])
                
        # Store all channels for filtering
        self.all_channels = [channel_info['display_name'] for channel_info in combined_channels.values()]
        
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
            
        # Generate default filename based on earliest TDMS file
        if self.tdms_files:
            # Sort files by name and use the earliest (first) one for naming
            sorted_files = sorted(self.tdms_files, key=lambda x: x['name'])
            base_name = os.path.splitext(sorted_files[0]['name'])[0]
            
            if len(self.tdms_files) == 1:
                default_filename = f"{base_name}_export.csv"
            else:
                # Multiple files: indicate time range
                last_file = sorted_files[-1]['name']
                last_base = os.path.splitext(last_file)[0]
                default_filename = f"{base_name}_to_{last_base}_export.csv"
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
            
            # Add calculated timestamp column if requested
            if self.include_timestamp_var.get():
                timestamp_data = self.create_timestamp_column()
                if timestamp_data is not None:
                    export_data["Calculated_Timestamp"] = timestamp_data
            
            # Add selected channels
            channel_ids = list(self.channels_data.keys())
            for i in range(self.selected_listbox.size()):
                display_name = self.selected_listbox.get(i)
                
                # Find corresponding channel ID
                for channel_id, channel_info in self.channels_data.items():
                    if channel_info['display_name'] == display_name:
                        # Create column name based on user preference
                        if self.include_group_names_var.get():
                            # Use full display name: "Group - Channel"
                            clean_name = display_name.replace("/", "_").replace(" ", "_")
                            clean_name = clean_name.replace(".", "_").replace("-", "_")
                        else:
                            # Use only channel name
                            clean_name = channel_info['channel_name'].replace("/", "_").replace(" ", "_")
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
            
            # Get current settings if file exists
            current_settings = {}
            if os.path.exists(self.settings_file):
                try:
                    with open(self.settings_file, 'r') as f:
                        current_settings = json.load(f)
                except:
                    pass
            
            settings = {
                "last_selected_channels": selected_channels,
                "include_time_column": self.include_time_var.get(),
                "include_timestamp_column": self.include_timestamp_var.get(),
                "include_group_names": self.include_group_names_var.get(),
                "last_import_directory": current_settings.get("last_import_directory", os.getcwd())
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
            include_timestamp = settings.get("include_timestamp_column", False)
            include_group_names = settings.get("include_group_names", True)
            
            # Apply time column setting
            self.include_time_var.set(include_time)
            
            # Apply timestamp column setting
            self.include_timestamp_var.set(include_timestamp)
            
            # Apply group names setting
            self.include_group_names_var.set(include_group_names)
            
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
    
    def save_last_import_directory(self, directory):
        """Save the last used import directory"""
        try:
            # Load existing settings
            settings = {}
            if os.path.exists(self.settings_file):
                try:
                    with open(self.settings_file, 'r') as f:
                        settings = json.load(f)
                except:
                    pass
            
            # Update import directory
            settings["last_import_directory"] = directory
            
            # Save back to file
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save import directory: {e}")
    
    def get_last_import_directory(self):
        """Get the last used import directory or return current working directory"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    saved_dir = settings.get("last_import_directory")
                    # Check if the saved directory still exists
                    if saved_dir and os.path.exists(saved_dir):
                        return saved_dir
        except Exception as e:
            print(f"Warning: Could not load import directory: {e}")
        
        # Default to current working directory
        return os.getcwd()
    
    def create_timestamp_column(self):
        """Create a calculated timestamp column from MachineStatus - Timestamp channel"""
        try:
            # Look for the MachineStatus - Timestamp channel (combined data)
            timestamp_data = None
            
            # Search in channels_data for the timestamp channel
            for channel_id, channel_info in self.channels_data.items():
                # Check if this channel contains "MachineStatus - Timestamp" 
                if ("MachineStatus" in channel_info['group_name'] and 
                    "Timestamp" in channel_info['channel_name']):
                    timestamp_data = channel_info['data']
                    break
            
            if timestamp_data is None:
                print(f"Warning: MachineStatus - Timestamp channel not found")
                return None
            
            # Convert Excel epoch time to readable timestamps
            # Excel epoch starts at 1900-01-01, but has a leap year bug (treats 1900 as leap year)
            # So we need to subtract 2 days (1900-01-01 to 1899-12-30) and account for the bug
            excel_epoch = datetime(1899, 12, 30)  # Excel's actual epoch after accounting for the bug
            
            readable_timestamps = []
            for excel_time in timestamp_data:
                try:
                    # Convert Excel serial date to datetime
                    if pd.isna(excel_time) or excel_time == 0:
                        readable_timestamps.append("")
                    else:
                        # Excel time is in days since epoch
                        python_datetime = excel_epoch + timedelta(days=float(excel_time))
                        # Format as ISO string with milliseconds
                        readable_timestamps.append(python_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
                except (ValueError, TypeError, OverflowError) as e:
                    # Handle invalid timestamp values
                    readable_timestamps.append(f"Invalid: {excel_time}")
            
            return readable_timestamps
            
        except Exception as e:
            print(f"Error creating timestamp column: {e}")
            return None



if __name__ == "__main__":
    viewer = TDMSViewer()
    viewer.mainloop()