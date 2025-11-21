
## [3.1.0] - 2025-11-21

### Added

- Add support for Python3.14
- Add timeout option to CLI command fgt backup

### Changed

- Unpin typer version and fix cli tests
- Refactor tests
- Change default timeout for fgt backup to 60 seconds
- Change Typing from Optional and Union to Pipe (|) syntax which is more pythonic

### Removed

- Remove support for Python 3.9
