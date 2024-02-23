### Added

- Option `--raw` for `fmg get devices`
- Support for HTTP `PATCH` and `DELETE` method in FortiClientEMS

### Changed

- `fmg get devices` also shows ha nodes if device is a cluster
- Make `Fortinet.api()` more generic to support more methods
- Improve error handling and tests for `Fortinet.api()`


### Fixed

- Better handling of EMS license expiry evaluation
