import os
import pandas as pd
import json
from datetime import datetime, timedelta
from nptdms import TdmsFile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import threading
import queue

class TDMSViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TDMS Channel Selector & CSV Converter v1.3.0")
        self.geometry("1200x1000")
        self.resizable(True, True)
        
        # Initialize variables
        self.tdms_files = []  # List to store multiple TDMS files
        self.channels_data = {}
        self.all_channels = []  # Store all channel display names for filtering
        self.time_column = None
        self.time_column_name = None
        self.settings_file = os.path.join(os.getcwd(), "last_selection.json")
        
        # Preview pane variables
        self.preview_enabled = True
        self.max_preview_points = 10000
        self._update_timer = None
        self.preview_queue = queue.Queue()
        
        # Timespan control variables
        self.timespan_enabled = False
        self.timespan_start = ""
        self.timespan_end = ""
        self.timespan_use_for_export = False
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=3)  # Channel selection gets good space
        main_frame.rowconfigure(2, weight=1)  # Preview pane gets minimal space
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
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
        channels_frame = ttk.LabelFrame(main_frame, text="Channel Selection", padding="6")
        channels_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 5), ipady=8)
        channels_frame.columnconfigure(0, weight=1)
        channels_frame.columnconfigure(2, weight=1)
        channels_frame.rowconfigure(2, weight=1)
        # Set compact minimum height
        channels_frame.configure(height=280)
        
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
        
        self.available_listbox = tk.Listbox(available_frame, selectmode=tk.EXTENDED, height=6)
        self.available_listbox.grid(row=0, column=0, sticky="nsew")
        
        # Add placeholder text so frame is visible even without TDMS files
        self.available_listbox.insert(tk.END, "No TDMS files loaded - Add files to see channels")
        
        available_scrollbar = ttk.Scrollbar(available_frame, orient="vertical", command=self.available_listbox.yview)
        available_scrollbar.grid(row=0, column=1, sticky="ns")
        self.available_listbox.configure(yscrollcommand=available_scrollbar.set)
        
        # Control buttons - centered in the middle
        button_frame = ttk.Frame(channels_frame)
        button_frame.grid(row=2, column=1, padx=10, sticky="")
        
        ttk.Button(button_frame, text="Add >>", command=self.add_channels).pack(pady=3)
        ttk.Button(button_frame, text="Add All", command=self.add_all_channels).pack(pady=3)
        ttk.Button(button_frame, text="<< Remove", command=self.remove_channels).pack(pady=3)
        ttk.Button(button_frame, text="Remove All", command=self.remove_all_channels).pack(pady=3)
        
        # Selected channels
        ttk.Label(channels_frame, text="Selected Channels").grid(row=0, column=2, pady=(0, 5))
        
        # Selected channels listbox with scrollbar
        selected_frame = ttk.Frame(channels_frame)
        selected_frame.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=(5, 0))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(0, weight=1)
        
        self.selected_listbox = tk.Listbox(selected_frame, selectmode=tk.EXTENDED, height=6)
        self.selected_listbox.grid(row=0, column=0, sticky="nsew")
        
        # Add placeholder text so frame is visible
        self.selected_listbox.insert(tk.END, "Selected channels will appear here")
        
        selected_scrollbar = ttk.Scrollbar(selected_frame, orient="vertical", command=self.selected_listbox.yview)
        selected_scrollbar.grid(row=0, column=1, sticky="ns")
        self.selected_listbox.configure(yscrollcommand=selected_scrollbar.set)
        
        # Bind selection events for preview updates
        self.selected_listbox.bind('<<ListboxSelect>>', self.on_selection_changed)
        
        # Create preview pane under channel selection
        self.create_preview_pane(main_frame)
        
        # Export section
        export_frame = ttk.LabelFrame(main_frame, text="Export Options", padding="5")
        export_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
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
        status_bar.grid(row=4, column=0, sticky="ew", pady=(10, 0))

    def create_preview_pane(self, parent):
        """Create the signal preview pane with matplotlib integration"""
        # Ensure matplotlib uses proper backend for tkinter
        import matplotlib
        matplotlib.use('TkAgg')
        
        # Preview pane label frame - compact padding
        preview_frame = ttk.LabelFrame(parent, text="Signal Preview", padding="3")
        preview_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        # Configure column weights to distribute space properly
        controls_frame.columnconfigure(2, weight=1)  # Channel combo gets extra space
        controls_frame.columnconfigure(6, weight=1)  # Last column gets remaining space
        
        # Preview enable/disable checkbox
        self.preview_enabled_var = tk.BooleanVar(value=False)
        preview_checkbox = ttk.Checkbutton(controls_frame, text="Enable Preview", 
                                         variable=self.preview_enabled_var,
                                         command=self.toggle_preview)
        preview_checkbox.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Channel selection for preview
        ttk.Label(controls_frame, text="Channel:").grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        self.preview_channel_var = tk.StringVar(value="First Selected")
        self.preview_channel_combo = ttk.Combobox(controls_frame, textvariable=self.preview_channel_var,
                                                state="readonly", width=25)
        self.preview_channel_combo.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        self.preview_channel_combo.bind('<<ComboboxSelected>>', self.on_preview_channel_changed)
        
        # Sample size control
        ttk.Label(controls_frame, text="Max Points:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.sample_size_var = tk.StringVar(value="10000")
        sample_entry = ttk.Entry(controls_frame, textvariable=self.sample_size_var, width=8)
        sample_entry.grid(row=0, column=4, sticky=tk.W)
        sample_entry.bind('<Return>', self.on_sample_size_changed)
        
        # Calculated timestamp option for preview
        self.preview_use_timestamp_var = tk.BooleanVar(value=False)
        timestamp_checkbox = ttk.Checkbutton(controls_frame, text="Show calculated timestamp",
                                           variable=self.preview_use_timestamp_var,
                                           command=self.update_preview)
        timestamp_checkbox.grid(row=0, column=5, sticky=tk.W, padx=(10, 0))
        
        # Second row for timespan controls
        controls_frame.rowconfigure(1, weight=0)
        
        # Timespan enable checkbox
        self.timespan_enabled_var = tk.BooleanVar(value=False)
        timespan_checkbox = ttk.Checkbutton(controls_frame, text="Limit time range",
                                           variable=self.timespan_enabled_var,
                                           command=self.on_timespan_enabled_changed)
        timespan_checkbox.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Start time entry
        ttk.Label(controls_frame, text="Start:").grid(row=1, column=1, sticky=tk.W, padx=(10, 2), pady=(5, 0))
        self.timespan_start_var = tk.StringVar()
        self.timespan_start_entry = ttk.Entry(controls_frame, textvariable=self.timespan_start_var, 
                                            width=12, state="disabled")
        self.timespan_start_entry.grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.timespan_start_var.trace('w', self.on_timespan_changed)
        
        # End time entry
        ttk.Label(controls_frame, text="End:").grid(row=1, column=3, sticky=tk.W, padx=(0, 2), pady=(5, 0))
        self.timespan_end_var = tk.StringVar()
        self.timespan_end_entry = ttk.Entry(controls_frame, textvariable=self.timespan_end_var, 
                                          width=12, state="disabled")
        self.timespan_end_entry.grid(row=1, column=4, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.timespan_end_var.trace('w', self.on_timespan_changed)
        
        # Refresh timespan button
        self.timespan_refresh_button = ttk.Button(controls_frame, text="Reset", width=6,
                                                command=self.refresh_timespan_suggestions,
                                                state="disabled")
        self.timespan_refresh_button.grid(row=1, column=5, sticky=tk.W, padx=(0, 8), pady=(5, 0))
        
        # Use for export checkbox
        self.timespan_use_for_export_var = tk.BooleanVar(value=False)
        export_checkbox = ttk.Checkbutton(controls_frame, text="Use for export",
                                         variable=self.timespan_use_for_export_var,
                                         state="disabled")
        export_checkbox.grid(row=1, column=6, sticky="ew", padx=(0, 5), pady=(5, 0))
        
        # Store references to timespan widgets for enabling/disabling
        self.timespan_widgets = [
            self.timespan_start_entry,
            self.timespan_end_entry, 
            self.timespan_refresh_button,
            export_checkbox
        ]
        
        # Create matplotlib figure and canvas - compact size
        self.preview_figure = Figure(figsize=(8, 3), dpi=80, facecolor='white')
        self.preview_axis = self.preview_figure.add_subplot(111)
        self.preview_axis.set_title("Select a channel to preview")
        self.preview_axis.grid(True, alpha=0.3)
        
        # Create canvas and toolbar
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.grid(row=1, column=0, sticky="nsew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.preview_canvas = FigureCanvasTkAgg(self.preview_figure, canvas_frame)
        self.preview_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Navigation toolbar
        toolbar_frame = ttk.Frame(preview_frame)
        toolbar_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        
        self.preview_toolbar = NavigationToolbar2Tk(self.preview_canvas, toolbar_frame)
        self.preview_toolbar.update()
        
        # Status label for preview
        self.preview_status_var = tk.StringVar(value="Preview ready")
        preview_status = ttk.Label(preview_frame, textvariable=self.preview_status_var, 
                                 font=('TkDefaultFont', 8))
        preview_status.grid(row=3, column=0, sticky="ew", pady=(2, 0))

    def toggle_preview(self):
        """Toggle preview pane on/off"""
        if self.preview_enabled_var.get():
            self.update_preview()
        else:
            self.clear_preview()
    
    def on_selection_changed(self, event=None):
        """Handle selection change in selected channels listbox"""
        if not self.preview_enabled_var.get():
            return
            
        # Cancel pending updates
        if self._update_timer:
            self.after_cancel(self._update_timer)
        
        # Update channel combo options
        self.update_preview_channel_options()
        
        # Schedule preview update with debouncing
        self._update_timer = self.after(300, self.update_preview_delayed)
    
    def on_preview_channel_changed(self, event=None):
        """Handle preview channel selection change"""
        if self.preview_enabled_var.get():
            self.update_preview()
    
    def on_sample_size_changed(self, event=None):
        """Handle sample size change"""
        try:
            new_size = int(self.sample_size_var.get())
            if new_size > 0:
                self.max_preview_points = new_size
                if self.preview_enabled_var.get():
                    self.update_preview()
        except ValueError:
            # Reset to current value if invalid
            self.sample_size_var.set(str(self.max_preview_points))
    
    def update_preview_channel_options(self):
        """Update the channel dropdown with currently selected channels"""
        selected_channels = []
        for i in range(self.selected_listbox.size()):
            selected_channels.append(self.selected_listbox.get(i))
        
        # Add special options
        options = ["First Selected", "Last Selected"]
        options.extend(selected_channels)
        
        self.preview_channel_combo['values'] = options
        
        # Keep current selection if still valid, otherwise reset to first
        current = self.preview_channel_var.get()
        if current not in options and options:
            self.preview_channel_var.set(options[0])
    
    def update_preview_delayed(self):
        """Delayed preview update to avoid excessive calls"""
        self._update_timer = None
        self.update_preview()
    
    def update_preview(self):
        """Update the preview plot with selected channel data"""
        if not self.preview_enabled_var.get() or not self.channels_data:
            return
        
        try:
            # Get selected channel for preview
            channel_to_preview = self.get_preview_channel()
            if not channel_to_preview:
                self.clear_preview("No channels selected")
                return
            
            # Find channel data
            channel_data = None
            for channel_id, channel_info in self.channels_data.items():
                if channel_info['display_name'] == channel_to_preview:
                    channel_data = channel_info['data']
                    break
            
            if channel_data is None:
                self.clear_preview("Channel data not found")
                return
            
            # Prepare time/index data
            if self.preview_use_timestamp_var.get():
                # Use calculated timestamp if requested and available
                timestamp_data = self.create_timestamp_column()
                if timestamp_data and len(timestamp_data) == len(channel_data):
                    try:
                        # Convert timestamp strings to datetime objects for plotting
                        x_data = []
                        for ts_str in timestamp_data:
                            if ts_str and not ts_str.startswith("Invalid"):
                                try:
                                    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
                                    x_data.append(dt)
                                except ValueError:
                                    # Try without microseconds
                                    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                                    x_data.append(dt)
                            else:
                                x_data.append(None)
                        
                        # Remove None values and corresponding channel data
                        valid_indices = [i for i, x in enumerate(x_data) if x is not None]
                        if valid_indices:
                            x_data = [x_data[i] for i in valid_indices]
                            channel_data = [channel_data[i] for i in valid_indices]
                            x_label = "Calculated Timestamp"
                        else:
                            raise ValueError("No valid timestamps found")
                            
                    except Exception as e:
                        # Fallback if timestamp conversion fails
                        if self.time_column and len(self.time_column) == len(channel_data):
                            x_data = self.time_column
                            x_label = self.time_column_name or "Time"
                        else:
                            x_data = list(range(len(channel_data)))
                            x_label = "Index (Timestamp conversion failed)"
                else:
                    # Fallback to regular time or index
                    if self.time_column and len(self.time_column) == len(channel_data):
                        x_data = self.time_column
                        x_label = self.time_column_name or "Time"
                    else:
                        x_data = list(range(len(channel_data)))
                        x_label = "Index (Timestamp not available)"
            elif self.time_column and len(self.time_column) == len(channel_data):
                x_data = self.time_column
                x_label = self.time_column_name or "Time"
            else:
                x_data = list(range(len(channel_data)))
                x_label = "Index"
            
            # Apply timespan filtering if enabled
            timespan_info = ""
            if self.timespan_enabled_var.get():
                original_count = len(x_data)
                start_str = self.timespan_start_var.get().strip()
                end_str = self.timespan_end_var.get().strip()
                
                try:
                    x_data, channel_data = self.filter_data_by_timespan(x_data, channel_data)
                    filtered_count = len(x_data)
                    
                    if filtered_count != original_count:
                        timespan_info = f" (filtered {original_count} to {filtered_count} points)"
                    elif filtered_count == 0:
                        self.clear_preview(f"No data in timespan range: {start_str} to {end_str}")
                        return
                except Exception as e:
                    # If filtering fails, show error but continue with unfiltered data
                    timespan_info = f" (filter error: {str(e)[:30]}...)"
            
            # Apply data sampling if needed
            if len(channel_data) > self.max_preview_points:
                x_data, channel_data = self.sample_data(x_data, channel_data)
                sample_info = f" (sampled to {len(channel_data)} points)"
            else:
                sample_info = ""
            
            # Clear and plot
            self.preview_axis.clear()
            self.preview_axis.plot(x_data, channel_data, 'b-', linewidth=1, alpha=0.8)
            
            # Format plot
            self.preview_axis.set_title(f"{channel_to_preview}{timespan_info}{sample_info}")
            self.preview_axis.set_xlabel(x_label)
            self.preview_axis.set_ylabel("Value")
            self.preview_axis.grid(True, alpha=0.3)
            
            # Format x-axis for timestamps
            if x_label == "Calculated Timestamp" and len(x_data) > 0:
                self.preview_axis.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                self.preview_axis.xaxis.set_major_locator(MaxNLocator(6))
                # Rotate labels for better readability  
                for label in self.preview_axis.xaxis.get_majorticklabels():
                    label.set_rotation(45)
                    label.set_horizontalalignment('right')
            
            # Auto-scale and refresh
            self.preview_axis.relim()
            self.preview_axis.autoscale()
            self.preview_figure.tight_layout()
            self.preview_canvas.draw()
            
            self.preview_status_var.set(f"Showing {len(channel_data)} points{timespan_info}{sample_info}")
            
        except Exception as e:
            self.clear_preview(f"Preview error: {str(e)}")
    
    def get_preview_channel(self):
        """Get the channel name to preview based on current selection"""
        selected_count = self.selected_listbox.size()
        if selected_count == 0:
            return None
        
        choice = self.preview_channel_var.get()
        
        if choice == "First Selected":
            return self.selected_listbox.get(0)
        elif choice == "Last Selected":
            return self.selected_listbox.get(selected_count - 1)
        else:
            # Specific channel selected
            return choice
    
    def sample_data(self, x_data, y_data):
        """Apply intelligent sampling to reduce data points while preserving characteristics"""
        if len(y_data) <= self.max_preview_points:
            return x_data, y_data
        
        # Calculate sampling step
        step = len(y_data) / self.max_preview_points
        
        # Use numpy for efficient sampling
        indices = np.linspace(0, len(y_data) - 1, self.max_preview_points, dtype=int)
        
        sampled_x = [x_data[i] for i in indices]
        sampled_y = [y_data[i] for i in indices]
        
        return sampled_x, sampled_y
    
    def clear_preview(self, message="Preview cleared"):
        """Clear the preview plot and show message"""
        self.preview_axis.clear()
        self.preview_axis.set_title(message)
        self.preview_axis.grid(True, alpha=0.3)
        self.preview_figure.tight_layout()
        self.preview_canvas.draw()
        self.preview_status_var.set(message)
    
    def suggest_timespan_defaults(self):
        """Suggest default timespan values based on current data"""
        if not self.channels_data or not self.time_column:
            return None, None
        
        try:
            # Get time data for analysis
            time_data = self.time_column
            if not time_data or len(time_data) < 2:
                return None, None
            
            # Determine if we're working with timestamps or numeric data
            first_time = time_data[0]
            last_time = time_data[-1]
            total_points = len(time_data)
            
            if isinstance(first_time, datetime) and isinstance(last_time, datetime):
                # Working with datetime objects
                total_duration = last_time - first_time
                # Suggest first 10% and last 90% as a reasonable middle range
                start_offset = total_duration * 0.1
                end_offset = total_duration * 0.9
                
                suggested_start = first_time + start_offset
                suggested_end = first_time + end_offset
                
                return (suggested_start.strftime("%H:%M:%S"), 
                       suggested_end.strftime("%H:%M:%S"))
            
            elif isinstance(first_time, (int, float)):
                # Working with numeric data (seconds or indices)
                total_range = last_time - first_time
                # Suggest middle 80% of the data range
                start_offset = total_range * 0.1
                end_offset = total_range * 0.9
                
                suggested_start = first_time + start_offset
                suggested_end = first_time + end_offset
                
                # Always return numeric values to match the data type
                # This ensures type compatibility in filtering
                return f"{suggested_start:.2f}", f"{suggested_end:.2f}"
            
        except Exception as e:
            # Silently handle errors in timespan suggestion
            return None, None
        
        return None, None
    
    def refresh_timespan_suggestions(self):
        """Manually refresh timespan suggestions with current data"""
        if not self.timespan_enabled_var.get():
            return
        
        suggested_start, suggested_end = self.suggest_timespan_defaults()
        
        if suggested_start and suggested_end:
            self.timespan_start_var.set(suggested_start)
            self.timespan_end_var.set(suggested_end)
            self.preview_status_var.set(f"Updated timespan: {suggested_start} to {suggested_end}")
            
            # Trigger preview update
            if self.preview_enabled_var.get():
                self.update_preview()
        else:
            self.preview_status_var.set("No data available for timespan suggestions")
    
    def on_timespan_enabled_changed(self):
        """Handle timespan enable/disable checkbox change"""
        enabled = self.timespan_enabled_var.get()
        
        # Enable/disable timespan widgets
        state = "normal" if enabled else "disabled"
        for widget in self.timespan_widgets:
            widget.config(state=state)
        
        # Show helpful information when enabled
        if enabled:
            # Auto-populate with suggested defaults if fields are empty
            if not self.timespan_start_var.get().strip() and not self.timespan_end_var.get().strip():
                suggested_start, suggested_end = self.suggest_timespan_defaults()
                
                if suggested_start and suggested_end:
                    self.timespan_start_var.set(suggested_start)
                    self.timespan_end_var.set(suggested_end)
                    self.preview_status_var.set(f"Auto-populated timespan: {suggested_start} to {suggested_end}")
                else:
                    formats = "Enter time range. Formats: 'YYYY-MM-DD HH:MM:SS', 'HH:MM:SS', 'MM:SS', or numeric seconds"
                    self.preview_status_var.set(formats)
            else:
                # Fields already have values, just validate
                self.validate_timespan_inputs()
        else:
            # Clear any validation messages when disabled
            if "timespan" in self.preview_status_var.get().lower() or "format" in self.preview_status_var.get().lower():
                self.preview_status_var.set("Preview ready")
        
        # Update preview if timespan is being enabled/disabled
        if self.preview_enabled_var.get():
            self.update_preview()
    
    def on_timespan_changed(self, *args):
        """Handle timespan start/end time changes"""
        if not self.timespan_enabled_var.get():
            return
        
        # Cancel pending updates
        if self._update_timer:
            self.after_cancel(self._update_timer)
        
        # Validate inputs and provide feedback
        self.validate_timespan_inputs()
        
        # Schedule preview update with debouncing
        self._update_timer = self.after(500, self.update_preview_delayed)
    
    def validate_timespan_inputs(self):
        """Validate timespan inputs and provide user feedback"""
        start_str = self.timespan_start_var.get().strip()
        end_str = self.timespan_end_var.get().strip()
        
        # Reset entry background colors to normal
        self.timespan_start_entry.config(style="TEntry")
        self.timespan_end_entry.config(style="TEntry")
        
        validation_message = ""
        
        # Parse inputs
        start_value = self.parse_timespan_input(start_str) if start_str else None
        end_value = self.parse_timespan_input(end_str) if end_str else None
        
        # Validate start input
        if start_str and start_value is None:
            try:
                # Create error style if it doesn't exist
                style = ttk.Style()
                style.map("Error.TEntry", fieldbackground=[('!focus', '#ffcccc')])
                self.timespan_start_entry.config(style="Error.TEntry")
            except:
                pass
            validation_message += "Invalid start time format. "
        
        # Validate end input
        if end_str and end_value is None:
            try:
                style = ttk.Style()
                style.map("Error.TEntry", fieldbackground=[('!focus', '#ffcccc')])
                self.timespan_end_entry.config(style="Error.TEntry")
            except:
                pass
            validation_message += "Invalid end time format. "
        
        # Validate logical relationship
        if start_value is not None and end_value is not None:
            try:
                # Compare values if they are the same type
                if type(start_value) == type(end_value):
                    comparison_valid = False
                    if isinstance(start_value, datetime) and isinstance(end_value, datetime):
                        comparison_valid = start_value >= end_value
                    elif isinstance(start_value, (int, float)) and isinstance(end_value, (int, float)):
                        comparison_valid = start_value >= end_value
                    
                    if comparison_valid:
                        validation_message += "Start time must be before end time. "
                        try:
                            style = ttk.Style()
                            style.map("Error.TEntry", fieldbackground=[('!focus', '#ffdddd')])
                            self.timespan_start_entry.config(style="Error.TEntry")
                            self.timespan_end_entry.config(style="Error.TEntry")
                        except:
                            pass
                else:
                    # Different types - note this for user
                    validation_message += "Start and end times have different formats. "
            except Exception:
                # If comparison fails, just note it
                validation_message += "Cannot compare start and end times. "
        
        # Update preview status with validation info
        if validation_message:
            self.preview_status_var.set(f"Timespan validation: {validation_message.strip()}")
        elif start_str or end_str:
            # Show helpful format information
            formats = "Formats: 'YYYY-MM-DD HH:MM:SS', 'HH:MM:SS', 'MM:SS', or numeric seconds"
            self.preview_status_var.set(f"Timespan ready. {formats}")
        
        return len(validation_message) == 0
    
    def parse_timespan_input(self, timespan_str):
        """Parse timespan input string to datetime object or numeric value"""
        if not timespan_str.strip():
            return None
        
        timespan_str = timespan_str.strip()
        
        # Try to parse as numeric value first (most common case for TDMS time data)
        try:
            numeric_value = float(timespan_str)
            return numeric_value
        except ValueError:
            pass
        
        # Try to parse as time formats and convert to seconds
        time_formats = [
            "%H:%M:%S.%f",           # Time only with microseconds  
            "%H:%M:%S",              # Time only
            "%M:%S.%f",              # Minutes and seconds with microseconds
            "%M:%S",                 # Minutes and seconds
        ]
        
        for fmt in time_formats:
            try:
                time_obj = datetime.strptime(timespan_str, fmt).time()
                # Convert to total seconds from midnight
                total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000
                return total_seconds
            except ValueError:
                continue
        
        # Try to parse as full datetime formats
        datetime_formats = [
            "%Y-%m-%d %H:%M:%S.%f",  # Full timestamp with microseconds
            "%Y-%m-%d %H:%M:%S",     # Full timestamp
        ]
        
        for fmt in datetime_formats:
            try:
                return datetime.strptime(timespan_str, fmt)
            except ValueError:
                continue
        
        # Try to parse as numeric value (seconds, index, etc.)
        try:
            return float(timespan_str)
        except ValueError:
            pass
        
        return None
    
    def filter_data_by_timespan(self, x_data, y_data, start_value=None, end_value=None):
        """Filter data arrays based on timespan values"""
        if not x_data or not y_data or len(x_data) != len(y_data):
            return x_data, y_data
        
        # Parse timespan inputs
        if start_value is None:
            start_str = self.timespan_start_var.get().strip()
            start_value = self.parse_timespan_input(start_str) if start_str else None
        
        if end_value is None:
            end_str = self.timespan_end_var.get().strip()
            end_value = self.parse_timespan_input(end_str) if end_str else None
        
        if start_value is None and end_value is None:
            return x_data, y_data
        
        # Convert x_data to comparable format
        comparable_x = []
        for x_val in x_data:
            if isinstance(x_val, datetime):
                comparable_x.append(x_val)
            elif isinstance(x_val, (int, float)):
                comparable_x.append(float(x_val))
            else:
                try:
                    # Try to convert to float for numeric comparison
                    comparable_x.append(float(x_val))
                except (ValueError, TypeError):
                    # If conversion fails, use index-based filtering
                    comparable_x.append(float(len(comparable_x)))
        
        # Convert everything to numeric for simpler comparison
        # This avoids complex type mixing issues
        numeric_x = []
        numeric_start = None
        numeric_end = None
        reference_time = None
        
        # Find reference time if we have datetime data
        for x_val in comparable_x:
            if isinstance(x_val, datetime):
                reference_time = x_val
                break
        
        # Convert x_data to numeric values
        for x_val in comparable_x:
            if isinstance(x_val, datetime) and reference_time:
                # Convert datetime to seconds from first datetime
                if x_val == reference_time:
                    numeric_x.append(0.0)
                else:
                    numeric_x.append((x_val - reference_time).total_seconds())
            elif isinstance(x_val, (int, float)):
                numeric_x.append(float(x_val))
            else:
                # Fallback for unknown types - use index
                numeric_x.append(float(len(numeric_x)))
        
        # Convert start/end values to numeric
        if start_value is not None:
            if isinstance(start_value, datetime) and reference_time:
                numeric_start = (start_value - reference_time).total_seconds()
            elif isinstance(start_value, (int, float)):
                numeric_start = float(start_value)
            else:
                numeric_start = 0.0  # Default start
        
        if end_value is not None:
            if isinstance(end_value, datetime) and reference_time:
                numeric_end = (end_value - reference_time).total_seconds()
            elif isinstance(end_value, (int, float)):
                numeric_end = float(end_value)
            else:
                numeric_end = float('inf')  # Default end
        
        # Apply filtering with numeric comparisons
        filtered_indices = []
        for i, x_numeric in enumerate(numeric_x):
            include = True
            
            if numeric_start is not None:
                include = include and (x_numeric >= numeric_start)
            
            if numeric_end is not None:
                include = include and (x_numeric <= numeric_end)
            
            if include:
                filtered_indices.append(i)
        
        # Return filtered data
        if not filtered_indices:
            return [], []
        
        filtered_x = [x_data[i] for i in filtered_indices]
        filtered_y = [y_data[i] for i in filtered_indices]
        
        return filtered_x, filtered_y

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
        
        # Restore placeholder text
        self.available_listbox.insert(tk.END, "No TDMS files loaded - Add files to see channels")
        self.selected_listbox.insert(tk.END, "Selected channels will appear here")
        
        # Update preview channel options and disable export button
        self.update_preview_channel_options()
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
        
        # Update preview channel options
        self.update_preview_channel_options()
        
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
        # Update preview channel options and trigger preview update
        self.update_preview_channel_options()
        self.update_preview()
        
    def add_all_channels(self):
        """Add all available channels to selected list"""
        # Clear selected list first
        self.selected_listbox.delete(0, tk.END)
        
        # Add all available channels
        for i in range(self.available_listbox.size()):
            item_text = self.available_listbox.get(i)
            self.selected_listbox.insert(tk.END, item_text)
            
        self.update_status()
        # Update preview channel options and trigger preview update
        self.update_preview_channel_options()
        self.update_preview()
        
    def remove_channels(self):
        """Remove selected channels from selected list"""
        selection = self.selected_listbox.curselection()
        if not selection:
            return
            
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            self.selected_listbox.delete(index)
            
        self.update_status()
        # Update preview channel options and trigger preview update
        self.update_preview_channel_options()
        self.update_preview()
        
    def remove_all_channels(self):
        """Remove all channels from selected list"""
        self.selected_listbox.delete(0, tk.END)
        self.update_status()
        # Update preview channel options and trigger preview update
        self.update_preview_channel_options()
        self.update_preview()
        
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
            
            # Apply timespan filtering if enabled and "Use for Export" is checked
            export_info = ""
            if (hasattr(self, 'timespan_enabled_var') and self.timespan_enabled_var.get() and 
                hasattr(self, 'timespan_use_for_export_var') and self.timespan_use_for_export_var.get()):
                
                try:
                    # Get the reference time data for filtering
                    reference_time_data = None
                    if self.time_column is not None:
                        reference_time_data = self.time_column
                    elif self.include_timestamp_var.get() and "Calculated_Timestamp" in export_data:
                        # Convert timestamp strings back to datetime objects for filtering
                        reference_time_data = []
                        for ts_str in export_data["Calculated_Timestamp"]:
                            if ts_str and not ts_str.startswith("Invalid"):
                                try:
                                    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f")
                                    reference_time_data.append(dt)
                                except ValueError:
                                    dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                                    reference_time_data.append(dt)
                            else:
                                reference_time_data.append(None)
                    
                    if reference_time_data:
                        # Create a dummy channel data list to get indices
                        dummy_data = list(range(len(reference_time_data)))
                        filtered_time, filtered_dummy = self.filter_data_by_timespan(reference_time_data, dummy_data)
                        
                        if len(filtered_dummy) > 0:
                            # Get the indices of filtered data
                            filtered_indices = filtered_dummy
                            original_count = len(reference_time_data)
                            
                            # Apply filtering to all export data columns
                            filtered_export_data = {}
                            for column_name, column_data in export_data.items():
                                if len(column_data) == original_count:
                                    filtered_export_data[column_name] = [column_data[i] for i in filtered_indices]
                                else:
                                    # Keep data as-is if length doesn't match
                                    filtered_export_data[column_name] = column_data
                            
                            export_data = filtered_export_data
                            export_info = f" (filtered to timespan: {len(filtered_indices)} of {original_count} points)"
                        else:
                            # No data in timespan - warn user but continue with full export
                            export_info = " (Warning: No data in specified timespan - exporting all data)"
                            
                except Exception as e:
                    # If filtering fails, continue with unfiltered export but warn user
                    export_info = f" (Timespan filtering failed: {str(e)[:50]}... - exporting all data)"
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            df.to_csv(output_file, index=False)
            
            # Save current selection for next time
            self.save_last_selection()
            
            messagebox.showinfo("Export Complete", 
                              f"Successfully exported {len(export_data)} columns to:\n{output_file}{export_info}")
            self.status_var.set(f"Export complete - {len(export_data)} columns saved{export_info}")
            
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
                "last_import_directory": current_settings.get("last_import_directory", os.getcwd()),

                "max_preview_points": getattr(self, 'max_preview_points', 10000),
                "preview_channel": getattr(self, 'preview_channel_var', tk.StringVar()).get(),
                "preview_use_timestamp": getattr(self, 'preview_use_timestamp_var', tk.BooleanVar()).get(),
                "timespan_enabled": getattr(self, 'timespan_enabled_var', tk.BooleanVar()).get(),
                "timespan_start": getattr(self, 'timespan_start_var', tk.StringVar()).get(),
                "timespan_end": getattr(self, 'timespan_end_var', tk.StringVar()).get(),
                "timespan_use_for_export": getattr(self, 'timespan_use_for_export_var', tk.BooleanVar()).get()
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

            max_preview_points = settings.get("max_preview_points", 10000)
            preview_channel = settings.get("preview_channel", "First Selected")
            preview_use_timestamp = settings.get("preview_use_timestamp", False)
            timespan_enabled = settings.get("timespan_enabled", False)
            timespan_start = settings.get("timespan_start", "")
            timespan_end = settings.get("timespan_end", "")
            timespan_use_for_export = settings.get("timespan_use_for_export", False)
            
            # Apply time column setting
            self.include_time_var.set(include_time)
            
            # Apply timestamp column setting
            self.include_timestamp_var.set(include_timestamp)
            
            # Apply group names setting
            self.include_group_names_var.set(include_group_names)
            
            # Apply preview settings
            # Preview enabled always defaults to False - not saved in settings
            if hasattr(self, 'max_preview_points'):
                self.max_preview_points = max_preview_points
                self.sample_size_var.set(str(max_preview_points))
            if hasattr(self, 'preview_channel_var'):
                self.preview_channel_var.set(preview_channel)
            if hasattr(self, 'preview_use_timestamp_var'):
                self.preview_use_timestamp_var.set(preview_use_timestamp)
            
            # Apply timespan settings
            if hasattr(self, 'timespan_enabled_var'):
                self.timespan_enabled_var.set(timespan_enabled)
            if hasattr(self, 'timespan_start_var'):
                self.timespan_start_var.set(timespan_start)
            if hasattr(self, 'timespan_end_var'):
                self.timespan_end_var.set(timespan_end)
            if hasattr(self, 'timespan_use_for_export_var'):
                self.timespan_use_for_export_var.set(timespan_use_for_export)
            
            # Update timespan widget states based on loaded settings
            if hasattr(self, 'timespan_widgets') and hasattr(self, 'timespan_enabled_var'):
                state = "normal" if self.timespan_enabled_var.get() else "disabled"
                for widget in self.timespan_widgets:
                    widget.config(state=state)
            
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
                
                # Update preview channel options after loading selection
                self.update_preview_channel_options()
                
                # Trigger preview update if preview is enabled
                if hasattr(self, 'preview_enabled_var') and self.preview_enabled_var.get():
                    self.update_preview()
                
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