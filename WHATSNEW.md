
## [3.0.0] - 2025-06-11

### Added

- Add FortiCloud module for FortiCloud Asset Management
- Add pylint checks for tests directory

### Changed

- CLI command "ems get workgroups" now displays group id in table
- Tool "ems get workgroups" has changed its return format
- Massive optimizations in cli help tests
- Typer cli commands now use typing_extensions.Annotated 
- Change typing for list, dict, set and tuple
- Update requests due to dependabot warning 

### Fixed

- Fixed some typos

### Removed

- Remove support for Python3.8
- Remove upper version bounds for external dependencies
