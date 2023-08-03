### Added

- First version of architecture documentation (according to Arc42)
- Inventory getter now supports wildcard * syntax
- Parallel processing bulk queries to FortiGates. This includes the following commands:
  `fgt backup` `fgt get version` `fgt monitor hamaster`
- Introduce `fgt config get` command to (bulk) print parts of saved configuration
- Command `fgt hamaster` now supports Jinja2 templating

### Changed

- Much better session key handling for FortiManager and FortiAnalyzer
- FortiManager and FortiAnalyzer session key can now be saved into a file
- Improved CHANGELOG and WHATSNEW handling for new releases
- `fgt monitor hamaster` now uses the API to query FortiGate instead of SNMP
- Migrate `fgt config`, `fgt get` and `fmg get` commands to use the Result class

### Removed

- Module pysnmp is not used anymore as we use API for all use cases now
