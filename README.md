# TDMS Channel Selector & CSV Converter

A user-friendly GUI application for selecting and exporting specific channels from TDMS (Technical Data Management Streaming) files to CSV format.

## 🚀 Features

### 📁 Multi-File Processing
- **Multiple TDMS file support**: Select and process multiple files as one continuous dataset
- **File management interface**: Add, remove, and organize TDMS files with intuitive controls
- **Chronological data merging**: Automatically concatenate data from sequential time spans
- **Smart filename generation**: Export names reflect time range from earliest to latest file

### 🎯 Smart Channel Selection
- Real-time channel filtering and search across all loaded files
- Dual-pane interface (Available ↔ Selected channels)
- Bulk operations (Add All/Remove All)
- Unified channel view treating multiple files as continuous dataset

### 📊 Flexible Export Options
- Include/exclude time/index columns with automatic merging across files
- Calculate readable timestamps from Excel epoch time (works with concatenated data)
- Choose to include/exclude group names in headers
- Automatic export folder management with intelligent naming

### 💾 Intelligent Memory
- Remembers your last channel selections across sessions
- Saves export preferences between sessions  
- Recalls last used import directory
- Maintains settings for multi-file workflows

### ⚡ User Experience
- Clean, resizable interface optimized for multi-file workflows
- Real-time status updates showing file count and channel information
- Comprehensive error handling with helpful messages
- Fast channel filtering and selection across combined datasets

## 📋 Quick Start

### Prerequisites
- Python 3.6 or higher
- Required Python packages (see Installation)

### Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install pandas nptdms
   ```

### Usage

1. **Run the application**:
   ```bash
   python tdms_viewer.py
   ```

2. **Add TDMS Files**: 
   - Click "Add TDMS Files..." to select one or multiple TDMS files
   - Files from the same system across different time periods are supported
   - Use "Remove Selected" or "Clear All" to manage your file list

3. **Filter Channels**: Use the filter box to find specific channels across all files

4. **Select Channels**: Use Add/Remove buttons to choose channels for export
   - Channels with the same name from different files are automatically combined
   - View shows unified channel list representing continuous timeline

5. **Configure Export**: Set your preferred export options
   - Include time/index columns (automatically merged across files)
   - Create calculated timestamps from combined data
   - Choose group name inclusion preferences

6. **Export**: Click "Export Selected Channels to CSV"
   - Single file exports use original filename with `_export` suffix
   - Multiple files create `earliest_to_latest_export.csv` format
   - All data is concatenated chronologically in output

## 📖 Export Options Guide

### Time Column
- **Include time/index column**: Adds timestamp or index data to CSV output

### Calculated Timestamp  
- **Create calculated timestamp column**: Converts Excel epoch timestamps to readable format
- Automatically finds "MachineStatus - Timestamp" channel across all loaded files
- Works with concatenated data from multiple files for continuous timeline
- Output format: `YYYY-MM-DD HH:MM:SS.mmm`

### Column Naming
- **Include group names**: Choose between `Group_Channel` vs `Channel` naming
- Helps avoid conflicts when multiple groups have similar channel names

## 📁 File Structure

```
crane_tdms_data/
├── tdms_viewer.py          # Main application with multi-file support
├── .gitignore             # Git ignore patterns  
├── CHANGELOG.md           # Version history and feature documentation
├── README.md              # This file - comprehensive usage guide
├── CONTRIBUTING.md        # Development guidelines and workflow
├── export/               # CSV output directory (auto-created)
└── last_selection.json    # User preferences (auto-generated)
```

## 🏷️ Version Information

**Current Stable**: v1.0.0  
**Development Branch**: feature/multi-file-support

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and upcoming features.

## 🛠️ Development

### Git Workflow

```bash
# Check current version
git tag -l

# Switch to development branch
git checkout feature/multi-file-support

# Switch back to stable
git checkout main
```

### Contributing

1. Create feature branch from `main`
2. Make changes and test thoroughly
3. Update CHANGELOG.md
4. Submit pull request

## 📋 Requirements

- **Python**: 3.6 or higher
- **Dependencies**: 
  - `pandas` - Data manipulation and CSV export
  - `nptdms` - TDMS file reading
  - `tkinter` - GUI framework (usually included with Python)

## 🐛 Known Issues

- Calculated timestamp only works with "MachineStatus - Timestamp" channel
- Large TDMS files may take time to load all channel data (affects multiple files)
- Very large datasets from multiple files may consume significant memory
- Files should have consistent channel structures for optimal merging

## 🔮 Upcoming Features (Future Development)

- Progress indicators for large multi-file operations
- Memory optimization for very large datasets  
- Advanced file validation and compatibility checking
- Custom data alignment options for mismatched time bases

## 📄 License

This project is provided as-is for internal use. Please ensure compliance with your organization's software usage policies.

## 📞 Support

For issues, feature requests, or questions:
- Check the [CHANGELOG.md](CHANGELOG.md) for known issues
- Review the Git commit history for recent changes
- Contact the development team