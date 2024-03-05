
## [2.1.0] - 2024-03-05

### Added

- Option `--raw` for `fmg get devices`
- Support for HTTP `PATCH` and `DELETE` method in FortiClientEMS
- Option `--smtp` for `fgt config check`


### Changed

- `fmg get devices` also shows ha nodes if device is a cluster
- Make `Fortinet.api()` more generic to support more methods
- Improve error handling and tests for `Fortinet.api()`
- Updated GitHub actions to latest major version due to Node.js 16 deprecation warning
- Use new dependency groups for Poetry in pyproject.toml
- Manage readthedocs dependencies with Poetry (instead of generated requirements.txt)

### Fixed

- Better handling of EMS license expiry evaluation
- Fix slicing on secrets output
- Better syntax for lists in documentation (developer/architecture/1_introduction_goals.html)
