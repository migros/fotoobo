### Added

- Option `--smtp` for `fmg assign` and `fmg_post`
- Method `inventory.get_item()` to only get one single item from the inventory

### Fixed

- Result.print_result_as_table() gives error with empty Response. Now it just prints an empty line
if no results were pushed.

### Changed

- `fortimanager.post()` now returns list of errors instead of just the number of errors

### Removed

