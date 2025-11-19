# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.3.0] - 2025-11-19

### Added
- **Timespan Controls**: Comprehensive time range filtering for preview and export operations
- **Smart Auto-Population**: Reset button with intelligent time range suggestions based on data analysis
- **Multiple Time Input Formats**: Support for `HH:MM:SS`, `MM:SS`, and numeric seconds input
- **Export Integration**: "Use for export" option to apply preview timespan to CSV exports
- **Real-time Validation**: Visual feedback for time input validation with helpful format hints
- **Enhanced Preview Initialization**: Improved channel selection handling and auto-updates
- **Settings Persistence**: Save and restore timespan preferences between sessions

### Changed
- **Preview Enabled State**: Always defaults to False at startup (no longer saved in settings)
- **Button Labeling**: Changed "Auto" to "Reset" for better user clarity
- **UI Layout**: Improved spacing and visibility of timespan controls
- **Version**: Updated to v1.3.0 stable release

### Fixed
- **Preview Update Issues**: Fixed preview not showing after loading saved channel selections
- **Type Handling**: Improved timespan filtering with better datetime/numeric type compatibility
- **UI Responsiveness**: Better handling of timespan widget enable/disable states

## [1.2.0] - 2025-11-18

### Added
- **Signal Preview Pane**: Interactive matplotlib-based signal plotting with full navigation
- **Channel Selection for Preview**: Choose any selected channel for individual preview
- **Calculated Timestamp Support**: Display human-readable timestamps in preview
- **Data Sampling**: Intelligent sampling for large datasets with configurable point limits
- **Preview Controls**: Enable/disable, channel selection, sample size, and timestamp options

### Changed
- **UI Layout**: Added preview pane with proper grid layout and resizing
- **Performance**: Optimized for large dataset handling with sampling

## [1.1.0] - 2025-11-14

### Added
- **Multi-file TDMS support**: Select and process multiple TDMS files as one continuous dataset
- **File management interface**: Add, remove, and manage multiple TDMS files with dedicated UI
- **Automatic data concatenation**: Chronologically combine channel data from multiple files
- **Smart export naming**: Generate filenames using earliest and latest file timestamps
- **Continuous timeline**: Merge time columns across files for uninterrupted data flow
- **System continuity**: Treat files from same system as sequential time spans
- **Comprehensive documentation**: Added CHANGELOG.md, README.md, and CONTRIBUTING.md

### Changed
- **File selection workflow**: Multi-file interface replaces single file browser
- **Data processing logic**: Multiple files processed as unified continuous dataset  
- **Export filename format**: Uses `earliest_to_latest_export.csv` for time ranges
- **Channel identification**: Simplified naming since files represent continuous operation
- **User interface layout**: Enhanced file management section with list and controls

### Removed
- Single file selection interface (replaced with comprehensive multi-file support)

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