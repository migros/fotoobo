"""
Test the convert module
"""

import pytest

from fotoobo.exceptions import GeneralError
from fotoobo.fortinet.convert import CheckpointConverter


def test_convert_hosts_type_not_present() -> None:
    """
    Test converting hosts when a supported type is not in the assets dict.
    """

    # Arrange
    assets = CheckpointConverter({})

    # Act & Assert
    with pytest.raises(GeneralError, match=r"type '.*' is not present in the infile"):
        assets.convert("hosts")


def test_convert_checkpoint_hosts_type_unsupported() -> None:
    """
    Test converting Checkpoint hosts when an unsupported type is given.
    """

    # Arrange
    assets = CheckpointConverter({})

    # Act & Assert
    with pytest.raises(GeneralError, match=r"type '.*' is not supported to convert"):
        assets.convert("unsupported")


def test_convert_checkpoint_hosts() -> None:
    """
    Test converting Checkpoint hosts.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "hosts": [
                {
                    "name": "host_name",
                    "comments": "host comment",
                    "ipv4-address": "10.20.30.40",
                    "uid": "1111-1111",
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("hosts")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "host_name",
                        "comment": "host comment",
                        "subnet": "10.20.30.40/32",
                        "uuid": "1111-1111",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/address/host_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_networks() -> None:
    """
    Test converting Checkpoint networks.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "networks": [
                {
                    "name": "network_name",
                    "comments": "network comment",
                    "subnet4": "10.20.30.0",
                    "mask-length4": 24,
                    "uid": "1111-1111",
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("networks")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "network_name",
                        "comment": "network comment",
                        "subnet": "10.20.30.0/24",
                        "uuid": "1111-1111",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/address/network_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_address_ranges() -> None:
    """
    Test converting Checkpoint address ranges.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "address_ranges": [
                {
                    "name": "range_name",
                    "comments": "range comment",
                    "ipv4-address-first": "10.20.30.44",
                    "ipv4-address-last": "10.20.30.55",
                    "uid": "1111-1111",
                    "dummy": "dummy",
                }
            ]
        }
    )
    # Act
    converted = assets.convert("address_ranges")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "range_name",
                        "comment": "range comment",
                        "type": "iprange",
                        "start-ip": "10.20.30.44",
                        "end-ip": "10.20.30.55",
                        "uuid": "1111-1111",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/address/range_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_groups() -> None:
    """
    Test converting Checkpoint groups.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "hosts": [{"uid": "1111-1111", "name": "member_1"}],
            "networks": [{"uid": "2222-2222", "name": "member_2"}],
            "address_ranges": [{"uid": "3333-3333", "name": "member_3"}],
            "groups": [
                {
                    "uid": "4444-4444",
                    "name": "group_name",
                    "comments": "group comment",
                    "members": ["1111-1111", "2222-2222", "3333-3333", "4444-4444"],
                    "dummy": "dummy",
                },
            ],
        }
    )

    # Act
    converted = assets.convert("groups")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "group_name",
                        "comment": "group comment",
                        "member": ["member_1", "member_2", "member_3", "group_name"],
                        "uuid": "4444-4444",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/addrgrp/group_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_groups_member_not_found() -> None:
    """
    Test converting Checkpoint groups when a member is not found.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "hosts": [{"uid": "11111111", "name": "member_1"}],
            "networks": [{"uid": "22222222", "name": "member_2"}],
            "address_ranges": [{"uid": "33333333", "name": "member_3"}],
            "groups": [
                {
                    "uid": "44444444",
                    "name": "group_name",
                    "comments": "group comment",
                    "members": ["55555555"],
                    "dummy": "dummy",
                },
            ],
        }
    )

    # Act
    converted = assets.convert("groups")

    # Assert
    assert not converted


def test_convert_checkpoint_services_icmp() -> None:
    """
    Test converting Checkpoint services icmp.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_icmp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "type": "service-icmp",
                    "icmp-type": 3,
                    "icmp-code": 3,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_icmp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "ICMP",
                        "icmptype": 3,
                        "icmpcode": 3,
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_icmp6() -> None:
    """
    Test converting Checkpoint services icmp6.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_icmp6": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "type": "service-icmp6",
                    "icmp-type": 3,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_icmp6")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "ICMP6",
                        "icmptype": 3,
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_tcp_single() -> None:
    """
    Test converting Checkpoint single tcp service.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_tcp": [
                {
                    "name": "service_name_1",
                    "comments": "service comment 1",
                    "port": "1111",
                    "use-default-session-timeout": False,
                    "session-timeout": 14400,
                    "dummy": "dummy",
                },
                {
                    "name": "service_name_2",
                    "comments": "service comment 2",
                    "port": "2222",
                    "use-default-session-timeout": False,
                    "session-timeout": 299,
                    "dummy": "dummy",
                },
            ]
        }
    )

    # Act
    converted = assets.convert("services_tcp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name_1",
                        "comment": "service comment 1",
                        "protocol": "TCP/UDP/SCTP",
                        "tcp-portrange": "1111",
                        "session-ttl": "14400",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name_1",
                },
                {
                    "data": {
                        "name": "service_name_2",
                        "comment": "service comment 2",
                        "protocol": "TCP/UDP/SCTP",
                        "tcp-portrange": "2222",
                        "session-ttl": "300",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name_2",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_tcp_range() -> None:
    """
    Test converting Checkpoint single tcp service.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_tcp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "port": "4444-5555",
                    "use-default-session-timeout": True,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_tcp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "TCP/UDP/SCTP",
                        "tcp-portrange": "4444-5555",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_tcp_gt() -> None:
    """
    Test converting Checkpoint tcp service with > syntax.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_tcp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "port": ">4444",
                    "use-default-session-timeout": True,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_tcp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "TCP/UDP/SCTP",
                        "tcp-portrange": "4445-65535",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_tcp_lt() -> None:
    """
    Test converting Checkpoint tcp service with < syntax.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_tcp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "port": "<4444",
                    "use-default-session-timeout": True,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_tcp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "TCP/UDP/SCTP",
                        "tcp-portrange": "1-4443",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_udp_single() -> None:
    """
    Test converting Checkpoint single udp service.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_udp": [
                {
                    "name": "service_name_1",
                    "comments": "service comment 1",
                    "port": "1111",
                    "use-default-session-timeout": False,
                    "session-timeout": 14400,
                    "dummy": "dummy",
                },
                {
                    "name": "service_name_2",
                    "comments": "service comment 2",
                    "port": "2222",
                    "use-default-session-timeout": False,
                    "session-timeout": 299,
                    "dummy": "dummy",
                },
            ]
        }
    )

    # Act
    converted = assets.convert("services_udp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name_1",
                        "comment": "service comment 1",
                        "protocol": "TCP/UDP/SCTP",
                        "udp-portrange": "1111",
                        "session-ttl": "14400",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name_1",
                },
                {
                    "data": {
                        "name": "service_name_2",
                        "comment": "service comment 2",
                        "protocol": "TCP/UDP/SCTP",
                        "udp-portrange": "2222",
                        "session-ttl": "300",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name_2",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_udp_range() -> None:
    """
    Test converting Checkpoint single udp service.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_udp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "port": "4444-5555",
                    "use-default-session-timeout": True,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_udp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "TCP/UDP/SCTP",
                        "udp-portrange": "4444-5555",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_udp_gt() -> None:
    """
    Test converting Checkpoint udp service with > syntax.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_udp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "port": ">4444",
                    "use-default-session-timeout": True,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_udp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "TCP/UDP/SCTP",
                        "udp-portrange": "4445-65535",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_services_udp_lt() -> None:
    """
    Test converting Checkpoint udp service with < syntax.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_udp": [
                {
                    "name": "service_name",
                    "comments": "service comment",
                    "port": "<4444",
                    "use-default-session-timeout": True,
                    "dummy": "dummy",
                }
            ]
        }
    )

    # Act
    converted = assets.convert("services_udp")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "service_name",
                        "comment": "service comment",
                        "protocol": "TCP/UDP/SCTP",
                        "udp-portrange": "1-4443",
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/custom/service_name",
                },
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_service_groups() -> None:
    """
    Test converting Checkpoint service groups.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_icmp": [{"uid": "11111111", "name": "member_1"}],
            "services_icmp6": [{"uid": "22222222", "name": "member_2"}],
            "services_tcp": [{"uid": "33333333", "name": "member_3"}],
            "services_udp": [{"uid": "44444444", "name": "member_4"}],
            "service_groups": [
                {
                    "uid": "55555555",
                    "name": "group_name",
                    "comments": "group comment",
                    "members": ["11111111", "22222222", "33333333", "44444444", "55555555"],
                    "dummy": "dummy",
                },
            ],
        }
    )

    # Act
    converted = assets.convert("service_groups")

    # Assert
    assert converted == [
        {
            "method": "set",
            "params": [
                {
                    "data": {
                        "name": "group_name",
                        "comment": "group comment",
                        "member": ["member_1", "member_2", "member_3", "member_4", "group_name"],
                    },
                    "url": "/pm/config/{adom}/obj/firewall/service/group/group_name",
                }
            ],
            "session": "",
            "id": 1,
        }
    ]


def test_convert_checkpoint_service_groups_member_not_found() -> None:
    """
    Test converting Checkpoint service groups when the member is not found.
    """

    # Arrange
    assets = CheckpointConverter(
        {
            "services_icmp": [{"uid": "11111111", "name": "member_1"}],
            "services_icmp6": [{"uid": "22222222", "name": "member_2"}],
            "services_tcp": [{"uid": "33333333", "name": "member_3"}],
            "services_udp": [{"uid": "44444444", "name": "member_4"}],
            "service_groups": [
                {
                    "uid": "55555555",
                    "name": "group_name",
                    "comments": "group comment",
                    "members": ["66666666"],
                    "dummy": "dummy",
                },
            ],
        }
    )

    # Act
    converted = assets.convert("service_groups")

    # Assert
    assert not converted
