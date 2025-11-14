# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Multi-file TDMS support**: Select and process multiple TDMS files as one continuous dataset
- **File management interface**: Add, remove, and manage multiple TDMS files with dedicated UI
- **Automatic data concatenation**: Chronologically combine channel data from multiple files
- **Smart export naming**: Generate filenames using earliest and latest file timestamps
- **Continuous timeline**: Merge time columns across files for uninterrupted data flow
- **System continuity**: Treat files from same system as sequential time spans

### Changed
- **File selection workflow**: Multi-file interface replaces single file browser
- **Data processing logic**: Multiple files processed as unified continuous dataset  
- **Export filename format**: Uses `earliest_to_latest_export.csv` for time ranges
- **Channel identification**: Simplified naming since files represent continuous operation
- **User interface layout**: Enhanced file management section with list and controls

### Deprecated

### Removed
- Single file selection interface (replaced with comprehensive multi-file support)

### Fixed

### Security

## [1.0.0] - 2025-11-14

### Added
- Interactive TDMS file selection and channel discovery
- Advanced filtering with real-time search functionality
- Dual-pane channel selection interface (Available ↔ Selected)
- Bulk operations (Add All/Remove All channels)
- Settings persistence for channel selections and preferences
- Directory memory for file import locations
- Flexible export options:
  - Include/exclude time/index columns
  - Calculated timestamp column from Excel epoch time
  - Include/exclude group names in column headers
- Smart CSV export with automatic folder creation
- Clean, resizable GUI with status feedback
- Comprehensive error handling

### Technical Features
- Excel epoch time conversion with leap year bug handling
- JSON-based configuration storage
- Cross-session memory for user preferences
- TDMS integration using nptdms library

### Dependencies
- Python 3.6+
- pandas
- nptdms  
- tkinter (included with Python)