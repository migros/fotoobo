### Added

- Add generic api_get() method in tools/fgt/get
- Add CLI command fgt get cmdb firewall address
- Add CLI command fgt get cmdb firewall addrgrp
- Add CLI command fgt get cmdb firewall service-custom
- Add CLI command fgt get cmdb firewall service-group
- Add the layers of fotoobo into the architecture documentation
- Support for Python3.13

### Changed

- Fix syslog format: we do not have to set PRI_VAL as it is calculated by SysLogHandler
- Fix some typing issues for Python3.8
- Optimize imports in CLI module
- Upgrade requests, jinja, pygount and virtualenv due to security issues and bugs
- Upgrade all dependencies to be up to date

### Removed

