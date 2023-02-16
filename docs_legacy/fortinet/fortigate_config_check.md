# FortiGate Configuration Check <span style="font-size:small">[[main](../../README.md)]</span>

The FortiGate configuration check module let's you check the configuration of a FortiGate configuration.

If a file is given it checks this file. If you pass a directory, it will do the checks for all the .conf files in this directory. Exciting, isn't it?

To have a good understanding on how fotoobo handles FortiGate configurations have a look at the [the FortiGate configuration structure](fortigate_config.md)

## Usage <span style="font-size:small">[[top](#)]</span>

```fotoobo fgt confcheck [configuration] [check_bundle]```

Arguments to pass:
  - _**configuration**_: FortiGate configuration object (file or directory)
  - _**check\_bundle**_: Fortigate check bundle (file)

## Check Bundles <span style="font-size:small">[[top](#)]</span>

A check bundle contains one ore more checks that are logically related to each other. These checks are defined by the individual fields for each entry in _checks_.

This section contains all check bundles which have been implemented in [fotoobo](../../README.md), you can incorporate them in your own bundles.

Note that you need one or more saved FortiGate configuration files to run these check against.

### General Bundle Options <span style="font-size:small">[[top](#)]</span>

Check bundles are written in [YAML](https://yaml.org/) files. Each bundle consists of these options:

- _**checks**_: The checks to perform. See examples.

- _**filter-config**_: Only perform the check if this config filter matches. As key you may give the configuration path. If the value at given path matches the check is executed. (It seems it doesn't work if scope is _vdom_ :-()

- _**filter-info**_: Only perform the check if the config information matches. As key you may give a key from configuration.info. If the value matches the check is executed. I may prefix the value with '<' or '>'

- _**name**_: (optional) this is the name of the check. If a name is given it is written to the results message so that it's easier to associate the results with the check bundle.

- _**path**_: The configuration path to check.

- _**scope**_: Whether to check the global or a vdom configuration. You can only set it to _global_ or _vdom_.

- _**type**_: this is the type of check to perform. The available checks are explained below in the section [check types](#check-types-top)


## Check Types <span style="font-size:small">[[top](#)]</span>

- [count](#count-top)
- [exist](#exist-top)
- [value](#value-top)
- [value_in_list](#value_in_list-top)

### count <span style="font-size:small">[[top](#)]</span>

This generic bundle checks the count of configuration parts in a configuration list. Use the following option in _checks_:

- _**lt**_: less than
- _**eq**_: equal to
- _**gt**_: greater that

Of course you can combine these options but it it only makes sense with _lt_ and _gt_.

```
- type: count
  name: <name>
  scope: <global or vdom>
  path: <path>
  filter-info:
    os_version: >6.2.0
  checks: 
    <comparing options>
```

**example**

```
- type: count
  name: check_1
  scope: global
  path: /system/ntp/ntp-server
  checks: 
    gt: 1
    lt: 11
```

### exist <span style="font-size:small">[[top](#)]</span>

This is a generic bundle which checks the presence of given configuration options. In _checks_ you may check if a key is present in the configuration with _true_ or if it is not present with _false_. Normally you would use this check with _false_ to see if a configuration option is not present (it's set to default). 

```
- type: exist
  name: <name>
  scope: <global or vdom>
  path: <path>
  checks: 
    <keys to check with true or false>
```

**example**

```
- type: exist
  name: check_1
  scope: global
  path: /system/global
  filter-config:
    /system/ha/mode: a-p
  checks: 
    admin-scp: true
    admintimeout: false
```


### value <span style="font-size:small">[[top](#)]</span>

This is a generic bundle which checks the presence and value of given configuration options. For the check to be successful the key MUST be present AND the value must match. Do not use this check to verify if a configuration option is default. Use [exist](#exist) with _false_ instead as default configuration options are not written to the configuration.

- _**ignore_missing**_: If you wish to ignore a missing configuration add the _ignore_missing_ flag and set it to _True_. This can be useful if the configuration option to check is not present on every FortiGate model.

```
- type: value
  name: <name>
  scope: <global or vdom>
  path: <path>
  ignore_missing: <bool>
  checks: 
    <key value pairs to check>
```

**example**

```
- type: value
  name: check_1
  scope: global
  path: /system/global
  checks: 
    admin-scp: enable
    admintimeout: 60
```


### value_in_list <span style="font-size:small">[[top](#)]</span>

This is a generic bundle which checks the presence and value of given configuration options in a configuration list. For the check to be successful the key MUST be present in any list item AND the value must match.

Special options are:

- _**inverse**_: set _inverse_ to search for non matching values

```
- type: value_in_list
  name: <name>
  scope: <global or vdom>
  path: <path>
  inverse: <bool, default:false>
  checks: 
    <key value pairs to check>
```

**example**
```
- type: value
  name: check_1
  scope: global
  path: /system/session-helper
  inverse: true
  checks: 
    name: sip
```
