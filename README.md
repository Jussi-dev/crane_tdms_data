# TDMS Channel Selector & CSV Converter

A user-friendly GUI application for selecting and exporting specific channels from TDMS (Technical Data Management Streaming) files to CSV format.

## 🚀 Features

### 🎯 Smart Channel Selection
- Interactive file browser for TDMS files
- Real-time channel filtering and search
- Dual-pane interface (Available ↔ Selected channels)
- Bulk operations (Add All/Remove All)

### 📊 Flexible Export Options
- Include/exclude time/index columns
- Calculate readable timestamps from Excel epoch time
- Choose to include/exclude group names in headers
- Automatic export folder management

### 💾 Intelligent Memory
- Remembers your last channel selections
- Saves export preferences between sessions
- Recalls last used import directory

### ⚡ User Experience
- Clean, resizable interface
- Real-time status updates
- Error handling with helpful messages
- Fast channel filtering and selection

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

1. Run the application:
   ```bash
   python tdms_viewer.py
   ```

2. **Select TDMS File**: Click "Browse..." to select a TDMS file

3. **Filter Channels**: Use the filter box to find specific channels

4. **Select Channels**: Use Add/Remove buttons to choose channels for export

5. **Configure Export**: Set your preferred export options

6. **Export**: Click "Export Selected Channels to CSV"

## 📖 Export Options Guide

### Time Column
- **Include time/index column**: Adds timestamp or index data to CSV output

### Calculated Timestamp  
- **Create calculated timestamp column**: Converts Excel epoch timestamps to readable format
- Automatically finds "MachineStatus - Timestamp" channel
- Output format: `YYYY-MM-DD HH:MM:SS.mmm`

### Column Naming
- **Include group names**: Choose between `Group_Channel` vs `Channel` naming
- Helps avoid conflicts when multiple groups have similar channel names

## 📁 File Structure

```
crane_tdms_data/
├── tdms_viewer.py          # Main application
├── .gitignore             # Git ignore patterns  
├── CHANGELOG.md           # Version history
├── README.md              # This file
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
- Large TDMS files may take time to load all channel data
- Duplicate column names possible when group names are excluded

## 🔮 Upcoming Features (Development Branch)

- Support for multiple TDMS files input
- Batch processing capabilities  
- Enhanced file management interface
- Improved performance for large datasets

## 📄 License

This project is provided as-is for internal use. Please ensure compliance with your organization's software usage policies.

## 📞 Support

For issues, feature requests, or questions:
- Check the [CHANGELOG.md](CHANGELOG.md) for known issues
- Review the Git commit history for recent changes
- Contact the development team