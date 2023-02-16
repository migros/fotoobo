# Changelog <span style="font-size:small">[[main](README.md)]</span>
 
All notable changes to this project will be documented in this file.
For examples and guidelines see [https://keepachangelog.com/](https://keepachangelog.com/)


## [Unreleased]

### Added

### Changed

- Update pytest to ~7.2.0 because of dependabot security warning


## [Released]


## [0.4.1] - 2023-02-06

### Changed

- Fix poetry dependencies with old poetry versions


## [0.4.0] - 2023-02-06

### Added

- Add Sphinx with autodoc for project documentation
- Verbose mode (-v) for fotoobo get version which also shows most important module versions
- Add jinja2 to dependencies for template handling
- Cli command "ems monitor ..." for several monitoring tasks (shouldn't it be moved to "ems get"?)
- print_dicttable to output helper (prints a dict as key/value table)
- LICENSE file and license clarification in README.md
- Lukas Murer is now also an author (thank you!)
- Helper variable "cli_path" for saving the complete cli command path
- Cli command "ems get workgroups"
- Option -V and --version addition to "get version"
- Sponsors section in README.md with Migros logo

### Changed

- Change and improve the logging handling
- print_datatable now pretty prints dicts and lists in values
- Changed smtp output to also send cli_path in body of e-mail 
- Typer callback functions now add the invoked_subcommand to the cli_path variable
- Optimize tox package handling
- Improve git caching mechanism
- Simplify get_version and update tests
- Structure of "fotoobo get" command
- Output of "get version" now in rich format
- Improve the fotoobo version test (testing with RegEx instead of hardcoded version)


## [0.3.1] - 2022-11-07

### Added

- Add timeout option for fmg assign

### Changed

- Change fmg assign to reflect reaching the timeout (no elapsed time, no history)


## [0.3.0] - 2022-11-07

### Added

- fmg get devices for getting logical devices from FortiManager
- fgt check subcommand
- fgt check hamaster: checks the HA master status from all Fortigate clusters in a FortiManager
- config: add the snmp_community setting (for use with easysnmp)

### Changed

- fmg assign now supports a comma separated list of ADOMs
- Removed redundancy in unit-tests for inventory.get() method (DRY)


## [0.2.1] - 2022-10-27

### Changed

- Downgrade the poetry version dependency from version =>1.2 to version =>1.1


## [0.2.0] - 2022-10-26

### Added

- Add caching logic for converted checkpoint assets
- Add Inventory.get() to get a list of devices from the inventory (DRY)
- fmg get policy with html output method for filterable table (thanks to Alex)
- Output class for collecting messages and send them in a bulk

### Changed

- Improve file_to_zip function (add level check and change return value to none)
- Change dev dependencies grouping in pyproject.toml
- Remove the login from the FortiManager and FortiClient EMS \_\_init\_\_()
- Move the smtp configuration from fotoobo.yaml to the inventory
- Use API for ems get version (instead of scraping login page)

## [0.1.0] - 2022-04-28
 
### Added
 
- Initial version with some basic features
- Support for following Fortinet devices: FortiGate, FortiManager, FortiAnalyzer, FortiClient EMS
 
### Changed

- Nothing yet
