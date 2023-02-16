"""The powerful convert module

Please refer to docs_legacy/convert_checkpoint_mappings.drawio.svg to see how a Checkpoint asset is
going to be converted into a Fortinet asset.

The Fortinet assets are referenced by their names. Even if we set a uuid we cannot use the uuid to
access the asset. The uuid is only supported for network assets and not for service assets.
"""

import copy
import logging
import os
from typing import Any, Dict, List, Optional

from fotoobo.exceptions import GeneralError
from fotoobo.helpers.files import load_json_file, save_json_file

log = logging.getLogger("fotoobo")


class CheckpointConverter:
    """
    The Checkpoint converter class
    """

    def __init__(self, assets: Any, cache_file: Optional[str] = None) -> None:
        self.assets = assets
        self.converted: List[Any] = []
        self.supported_types = [
            "hosts",
            "networks",
            "address_ranges",
            "groups",
            "services_icmp",
            "services_icmp6",
            "services_tcp",
            "services_udp",
            "service_groups",
        ]
        self.cache_file = cache_file

    def convert(self, obj_type: str, bulk_size: int = 100) -> List[Any]:
        """
        Convert Checkpoint configuration objects into Fortinet syntax.

        Args:
            assets (Any): the original assets
            obj_type (str): define the type of objects to convert
            bulk_size: the bulk size to generate

        Returns:
            List: the converted assets
        """

        # fix for bulk problem with groups:
        # It seems that adding groups in bulk mode does not work correctly. If one of the entries
        # in a bulk set is invalid all of them are not added with the same error.
        if obj_type == "groups":
            bulk_size = 1

        if obj_type not in self.supported_types:
            raise GeneralError(f"type '{obj_type}' is not supported to convert")

        if obj_type not in self.assets:
            raise GeneralError(f"type '{obj_type}' is not present in the infile")

        log.debug("converting asset type '%s'", obj_type)
        log.debug("found '%s' asset(s)", len(self.assets[obj_type]))
        assets = getattr(self, "_convert_" + obj_type)()

        # Now do the caching if cache_file is given
        if self.cache_file:
            cache: List[Any] = []
            if os.path.isfile(self.cache_file):
                log.debug("found cache file '%s'", self.cache_file)
                cache = list(load_json_file(self.cache_file) or [])

            save_json_file(self.cache_file, assets)
            assets = [asset for asset in assets if asset not in cache]
            log.debug("found '%s' new asset(s) not in cache", len(assets))

        # Now do the bulking
        i = 0
        params = []
        while assets:
            params.append(assets.pop(0))
            i += 1
            if i == bulk_size or not assets:
                converted = {
                    "method": "set",
                    "params": params,
                    "session": "",
                    "id": 1,
                }
                self.converted.append(converted)
                i = 0
                params = []

        return self.converted

    def _convert_hosts(self) -> Any:
        """
        Convert Checkpoint host objects

        Returns:
            Any: converted Fortinet objects
        """
        objects = self.assets["hosts"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            param = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "subnet": f"{obj['ipv4-address']}/32",
                    "uuid": obj["uid"],
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/address/{url_name}",
            }
            assets.append(param)

        return assets

    def _convert_networks(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint network objects

        Returns:
            list: converted Fortinet objects
        """
        objects = self.assets["networks"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            param = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "subnet": f"{obj['subnet4']}/{obj['mask-length4']}",
                    "uuid": obj["uid"],
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/address/{url_name}",
            }
            assets.append(param)

        return assets

    def _convert_address_ranges(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint address range objects

        Returns:
            list: converted Fortinet objects
        """
        objects = self.assets["address_ranges"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            param = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "type": "iprange",
                    "start-ip": f"{obj['ipv4-address-first']}",
                    "end-ip": f"{obj['ipv4-address-last']}",
                    "uuid": obj["uid"],
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/address/{url_name}",
            }
            assets.append(param)

        return assets

    def _convert_groups(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint group objects

        Returns:
            list: converted Fortinet objects
        """
        objects = copy.deepcopy(self.assets["groups"])
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            forti_members = []
            for uid in obj["members"]:
                found = False
                for obj_type in ["hosts", "networks", "address_ranges", "groups"]:
                    for net_object in self.assets[obj_type]:
                        if net_object["uid"] == uid:
                            forti_members.append(net_object["name"])
                            found = True
                if not found:
                    log.error("Object with uid %s not found", uid)

            param = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "member": forti_members,
                    "uuid": obj["uid"],
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/addrgrp/{url_name}",
            }
            if forti_members:
                assets.append(param)

            else:
                log.error("network group %s is empty", url_name)

        return assets

    def _convert_services_icmp(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint services_icmp objects

        Returns:
            list: converted Fortinet objects
        """
        objects = self.assets["services_icmp"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            param: Dict[str, Any] = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "protocol": "ICMP",
                    "icmptype": obj["icmp-type"],
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/service/custom/{url_name}",
            }
            if "icmp-code" in obj:
                param["data"]["icmpcode"] = obj["icmp-code"]

            assets.append(param)

        return assets

    def _convert_services_icmp6(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint services_icmp6 objects

        Returns:
            list: converted Fortinet objects
        """
        objects = self.assets["services_icmp6"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            param: Dict[str, Any] = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "protocol": "ICMP6",
                    "icmptype": obj["icmp-type"],
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/service/custom/{url_name}",
            }
            assets.append(param)

        return assets

    def _convert_services_tcp(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint services_tcp objects

        Possible values for "port" in the Checkpoint assets are:
        - "2000" is a single port which will be "2000"
        - "3000-3500" is a portrange which will be "3000-4000"
        - ">4000" will be converted to "4001-65535"
        - "<5000" will be converted to "1-4999"

        Returns:
            list: converted Fortinet objects
        """
        objects = self.assets["services_tcp"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            if obj["port"][0] == ">":
                port_range = str(int(obj["port"][1:]) + 1) + "-65535"
            elif obj["port"][0] == "<":
                port_range = "1-" + str(int(obj["port"][1:]) - 1)
            else:
                port_range = obj["port"]
            param: Dict[str, Any] = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "protocol": "TCP/UDP/SCTP",
                    "tcp-portrange": f"{port_range}",
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/service/custom/{url_name}",
            }
            if not obj["use-default-session-timeout"]:
                if (ttl := obj["session-timeout"]) < 300:  # FortiGate does not allow ttl < 300
                    ttl = 300
                param["data"]["session-ttl"] = str(ttl)

            assets.append(param)

        return assets

    def _convert_services_udp(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint services_udp objects
        Even though the UDP services are almost identical to the TCP services we use it's own
        convert function. This adds some redundancy but removes complexity and segregates duties.

        For possible values for the Checkpoint "port" field and how they will get converted refer
        to the _convert_services_tcp function.

        Returns:
            list: converted Fortinet objects
        """
        objects = self.assets["services_udp"]
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")
            if obj["port"][0] == ">":
                port_range = str(int(obj["port"][1:]) + 1) + "-65535"
            elif obj["port"][0] == "<":
                port_range = "1-" + str(int(obj["port"][1:]) - 1)
            else:
                port_range = obj["port"]
            param: Dict[str, Any] = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "protocol": "TCP/UDP/SCTP",
                    "udp-portrange": f"{port_range}",
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/service/custom/{url_name}",
            }
            if not obj["use-default-session-timeout"]:
                if (ttl := obj["session-timeout"]) < 300:  # FortiGate does not allow ttl < 300
                    ttl = 300
                param["data"]["session-ttl"] = str(ttl)

            assets.append(param)

        return assets

    def _convert_service_groups(self) -> List[Dict[str, Any]]:
        """
        Convert Checkpoint service group objects

        Returns:
            list: converted Fortinet objects
        """
        objects = copy.deepcopy(self.assets["service_groups"])
        assets = []
        while objects:
            obj = objects.pop(0)
            url_name = obj["name"].replace("/", "\\/")

            # patch for special group "gIntegrity_Server"
            # This one is not able to be converted as the members are not supported by FortiManager.
            # Remove the group "gIntegrity_Server" from the Checkpoint global policy (it seems not
            # to be in use). Then this patch can be removed.
            if url_name == "gIntegrity_Server":
                continue  # pragma: no cover

            forti_members = []
            for uid in obj["members"]:
                found = False
                for obj_type in [
                    "services_tcp",
                    "services_udp",
                    "services_icmp",
                    "services_icmp6",
                    "service_groups",
                ]:
                    for net_object in self.assets[obj_type]:
                        if net_object["uid"] == uid:
                            forti_members.append(net_object["name"])
                            found = True
                if not found:
                    log.error("Object with uid %s not found", uid)
            param = {
                "data": {
                    "comment": obj["comments"],
                    "name": obj["name"],
                    "member": forti_members,
                },
                "url": f"/pm/config/{{adom}}/obj/firewall/service/group/{url_name}",
            }
            if forti_members:
                assets.append(param)

            else:
                log.error("service group %s is empty", url_name)

        return assets
