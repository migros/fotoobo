# Changelog <span style="font-size:small">[[main](README.md)]</span>
 
All notable changes to this project will be documented in this file.
For examples and guidelines see [https://keepachangelog.com/](https://keepachangelog.com/)


# [Unreleased]

For unreleased changes see [WHATSNEW.md](WHATSNEW.md)

# [Released]

## [2.0.0] - 2023-11-28

### Added

- Support for Hashicorp Vault service to store sensitive inventory data
- Add license, repository and classifiers in pyproject.toml

### Changed

- Enhance create_dir() in files helper
- Change default logging (console logging enabled with log-level WARNING)

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

## [1.0.3] - 2023-08-17

### Added

- Add Python 3.12 pre release to GitHub actions for compatibility checking

### Changed

- Update dependency - certifi (2023.5.7 -> 2023.7.22)
- Logo path in README - now the logo is also displayed on PyPI

### Removed

## [1.0.2] - 2023-08-03

### Changed

- Improve new lines in WHATSNEW.md template

## [1.0.1] - 2023-08-03

### Changed

- Improve release process - WHATSNEW.md now handled correctly

## [1.0.0] - 2023-08-03

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


## [0.10.0] - 2023-06-15

### Added

- Add documentation about templating with jinja2
- Add documentation about how to import fotoobo into Python modules
- Add \_\_init\_\_ to the autodoc documentation
- Add raw option `-r` or `--raw` to cli commands for ems monitor

### Changed

- Beautify `ems monitor` commands output
- Optimize the way to import fotoobo in Python modules. For example you may now do
  `from fotoobo import FortiGate` instead of `from fotoobo.fortinet.fortigate import FortiGate`.
- Refactored whole code to use `pathlib.Path` instead of `os.path`
- Introduced a new `Result` class to abstract the output of the tools from the CLI print logic
  and started to migrate to this class for `ems monitor`, `fgt backup` and `convert` commands to 
  use it.
- The inventory will now be searched relative to the `fotoobo.yaml` if given by a relative path
  (instead of searching from the cwd, which can cause confusion)
- Update Sphinx to 6.2.1

### Fixed

- Fix pyasn1 to 0.4.8 due to pysnmp dependency
- Fix a bug with non existing cookie path for EMS
- Fix default values for jinja2 template helper


## [0.9.0] - 2023-04-23

### Added

- It is now possible to use a custom CA to verify the connections to your Fortinet devices


### Changed

- Command `fotoobo fmg assign` now lets you specify which global policy to assign
- Changed the order of arguments in `fotoobo fmg post` and made host optional with "fmg" as default.


## [0.8.0] - 2023-04-13

### Changed

- Renamed the following commands:
   - `fotoobo fmg set` -> `fotoobo fmg post`
   - `fotoobo fgt check` -> `fotoobo fgt monitor`
- Changed argument ordering of the following commands (since host is usually optional):
   - `fotoobo fmg assign`
   - `fotoobo fmg get policy`
- Invoking fotoobo (or any sub-command) without arguments displays the help instead of an error


## [0.7.0] - 2023-04-06

### Added

- Option `backup_dir` in CLI command `fgt backup`
- CLI command `fgt config info` to display information from FortiGate configuration file(s)

### Changed

- Update getting started guide
- Fix ordering of syslog message to comply with RFC5424
- Fix path handling with jinja2 templates (now support relative and absolute paths)

### Removed

- Global option `backup_dir` in fotoobo.yaml


## [0.6.1] - 2023-03-23

### Changed

- Fix the login issue with SFTP
- Fix permissions on .tag_release.sh


## [0.6.0] - 2023-03-23

### Added

- Add option to upload a backup file with sftp (which is now the default)
- New `globals` section in inventory to set global options for devices
- Define the port number to connect to a Fortinet API device with the new inventory option
  https_port
- fotoobo will now also search for a global config file in `~/.config/fotoobo.yaml`, if no explicit
  config file is given by command line parameter, or it does not find a `fotoobo.yaml` in the
  current working directory

### Changed

- Switch from easysnmp to pysnmp because pysnmp is pure Python
- Split the cli command `fgt` `confcheck` to subcommand: `fgt` `config` `check` as there will be
  more subcommands in the future


## [0.5.0] - 2023-03-02

### Added

- fotoobo is now on the official PyPI


## [0.4.3-6] - 2023-03-02

### Added

- GitHub actions to automatically deploy to (Test-)PyPi and create a GitHub release


## [0.4.2] - 2023-03-02

### Added

- Pull request rules on GitHub repo
- Possibility to make a release by script
- Add documentation to readthedocs.io as [fotoobo.readthedocs.io](https://fotoobo.readthedocs.io/)

### Changed

- Change traceback.txt to traceback.log
- Change syslog format to conform with RFC5424
- Move project from internal GIT to GitHub
- GitHub action to use multiple Python versions
- Update pytest to ~7.2.0 because of dependabot security warning
- Update tox, requests & pygount to get rid of module py


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
