# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for multiple TDMS files input with file selection dialog
- File list management interface with add/remove capabilities
- Automatic data concatenation from multiple files (chronological order)
- Smart export filename generation using earliest and latest file names
- Time column concatenation across multiple files for continuous timeline
- Channel data merging from same system across different time spans

### Changed
- File selection UI replaced with multi-file management interface
- Multiple TDMS files now treated as one continuous dataset
- Export naming uses earliest file with time range indication
- Data processing concatenates channels from all files chronologically
- Channel display simplified since files represent continuous data

### Deprecated

### Removed
- Single file selection interface (replaced with multi-file support)

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