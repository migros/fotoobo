### Added

- Option `--raw` for `fmg get devices`
- Option `--smtp` for `fgt config check`

### Changed

- `fmg get devices` also shows ha nodes if device is a cluster
- Updated GitHub actions to latest major version due to Node.js 16 deprecation warning

### Fixed

- Better handling of EMS license expiry evaluation
- Fix slicing on secrets output
- Better syntax for lists in documentation (developer/architecture/1_introduction_goals.html)
