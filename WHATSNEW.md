
## [1.1.0] - 2023-10-18

### Added

- Add support for Python 3.12
- Option `--smtp` for `fmg assign` and `fmg_post`
- Method `inventory.get_item()` to only get one single item from the inventory

### Fixed

- Add dev dependencies to docs requirements file (due to readthedocs build error)
- Update to urllib3 2.0.7 due to dependabot security warning
- No more Traceback for FortiGates without hostname or token specified
- Result.print_result_as_table() gives error with empty Response. Now it just prints an empty line
if no results were pushed.

### Changed

- Disable caching in Github Actions due to an error since Python 3.12
- `fortimanager.post()` now returns list of errors instead of just the number of errors
