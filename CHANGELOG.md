# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for multiple TDMS files input
- Batch processing capabilities
- File list management interface

### Changed

### Deprecated

### Removed

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