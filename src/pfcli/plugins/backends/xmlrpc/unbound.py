import json
from typing import Any
import xmlrpc.client as xc

from pfcli.consts import DEFAULT_TIMEOUT_IN_SECONDS
from pfcli.domain.unbound import entities
import pfcli.domain.unbound.api as api
from pfcli.shared.helpers import indent


def __parse_host_override_alias(alias: dict[str, str]) -> entities.HostOverride.Alias:
    return entities.HostOverride.Alias(
        host=alias["host"],
        domain=alias["domain"],
        description=alias["description"],
    )


def __parse_host_override_aliases(
    aliases: dict[str, Any]
) -> list[entities.HostOverride.Alias]:
    if "item" not in aliases:
        return []

    return list(map(__parse_host_override_alias, aliases["item"]))


def _parse_host_override(host: dict[str, Any]) -> entities.HostOverride:
    return entities.HostOverride(
        host=host["host"],
        domain=host["domain"],
        ip=host["ip"],
        description=host["descr"],
        aliases=__parse_host_override_aliases(host["aliases"]),
    )


def _dict_to_php_array(d: dict[str, str]) -> str:
    xs = [f'"{k}" => "{v}"' for k, v in d.items()]

    lines = ",\n".join(xs)

    return f"array(\n{indent(lines)}\n)"


# pylint: disable=too-few-public-methods
class CommandRunner:
    def __init__(self, proxy: xc.ServerProxy, timeout_in_seconds: float):
        self.__timeout_in_seconds = timeout_in_seconds
        self.__proxy = proxy

    def exec(self, commands: list[str]) -> str:
        return self.__proxy.pfsense.exec_php(
            "\n".join(commands), self.__timeout_in_seconds
        )  # type: ignore

    def apply_changes(self) -> None:

        self.exec(  # services_unbound.php
            [
                "$retval = 0;",
                "$retval |= services_unbound_configure();",
                "if ($retval == 0) { clear_subsystem_dirty('unbound'); }",
                "system_resolvconf_generate();",
                "system_dhcpleases_configure();",
                "$toreturn = 1;",
            ]
        )


class HostOverridesApi(api.UnboundApi.HostOverridesApi):
    def __init__(self, cr: CommandRunner):
        self.__cr = cr

    def list(self) -> list[entities.HostOverride]:
        hosts_r = self.__cr.exec(
            ["$toreturn = json_encode(config_get_path('unbound/hosts', []));"],
        )

        hosts = json.loads(hosts_r)

        return list(map(_parse_host_override, hosts))

    def add(
        self, override: entities.HostOverride, message_reason: str | None = None
    ) -> None:
        override_params = {
            "descr": override.description or "",
            "domain": override.domain,
            "host": override.host,
            "ip": override.ip,
            "aliases": _dict_to_php_array({}),
        }
        message_reason = (
            message_reason
            or f"Add host override {override.host}.{override.domain} {override.ip}"
        )

        self.__cr.exec(  # services_unbound_host_edit.php
            [
                f"$hostent = {_dict_to_php_array(override_params)};",
                # pylint: disable=line-too-long
                "config_set_path('unbound/hosts/' . count(config_get_path('unbound/hosts', [])) + 1, $hostent);",
                # "hosts_sort()", <- undefined function, available in services_ubound_host_edit.php
                "mark_subsystem_dirty('unbound');",
                f'write_config("{message_reason}");',
                "$toreturn = 1;",
            ]
        )

        self.__cr.apply_changes()

    def delete(self, index: int, message_reason: str | None = None) -> None:

        message_reason = message_reason or "Host override deleted from DNS Resolver."

        path_to_hosts = f"unbound/hosts/{index}"

        self.__cr.exec(  # services_unbound.php
            [
                f"if (config_get_path('{path_to_hosts}')) {{",
                f"config_del_path('{path_to_hosts}');",
                f'write_config("{message_reason}");',
                "mark_subsystem_dirty('unbound');",
                "}",
            ]
        )

        self.__cr.apply_changes()


# pylint: disable=too-few-public-methods
class UnboundApi(api.UnboundApi):
    def __init__(
        self,
        proxy: xc.ServerProxy,
        timeout_in_seconds: int = DEFAULT_TIMEOUT_IN_SECONDS,
    ):
        self.__host_overrides_api = HostOverridesApi(
            CommandRunner(proxy, timeout_in_seconds)
        )

    @property
    def host_overrides(self) -> api.UnboundApi.HostOverridesApi:
        return self.__host_overrides_api
