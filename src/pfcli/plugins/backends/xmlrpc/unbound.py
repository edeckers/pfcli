import json
from typing import Any
import xmlrpc.client as xc

from pfcli.consts import DEFAULT_TIMEOUT_IN_MILLISECONDS
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
class UnboundApi(api.UnboundApi):
    def __init__(
        self,
        proxy: xc.ServerProxy,
        timeout_in_milliseconds: int = DEFAULT_TIMEOUT_IN_MILLISECONDS,
    ):
        self.__proxy = proxy
        self.__timeout_in_seconds = timeout_in_milliseconds / 1_000

    def __exec_commands(self, commands: list[str]) -> str:
        return self.__proxy.pfsense.exec_php(
            "\n".join(commands), self.__timeout_in_seconds
        )  # type: ignore

    def host_overrides(self) -> list[entities.HostOverride]:
        hosts_r = self.__exec_commands(
            ["$toreturn = json_encode(config_get_path('unbound/hosts', []));"],
        )

        hosts = json.loads(hosts_r)

        return list(map(_parse_host_override, hosts))

    def host_override_add(
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

        commands_update = [  # services_unbound_host_edit.php
            f"$hostent = {_dict_to_php_array(override_params)};",
            # pylint: disable=line-too-long
            "config_set_path('unbound/hosts/' . count(config_get_path('unbound/hosts', [])) + 1, $hostent);",
            # "hosts_sort()", <- undefined function, available in services_ubound_host_edit.php
            "mark_subsystem_dirty('unbound');",
            f'write_config("{message_reason}");',
            "$toreturn = 1;",
        ]

        self.__exec_commands(commands_update)

        commands_apply = [  # services_unbound.php
            "$retval = 0;",
            "$retval |= services_unbound_configure();",
            "if ($retval == 0) { clear_subsystem_dirty('unbound'); }",
            "system_resolvconf_generate();",
            "system_dhcpleases_configure();",
            "$toreturn = 1;",
        ]

        self.__exec_commands(commands_apply)
