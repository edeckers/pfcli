import json
from typing import Any
import xmlrpc.client as xc

from pfcli.consts import DEFAULT_TIMEOUT_IN_MILLISECONDS
import pfcli.domain.unbound.entities as entities
import pfcli.domain.unbound.unbound as api
from pfcli.plugins.backends.xmlrpc.helpers import v


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

    return sorted(
        list(map(__parse_host_override_alias, aliases["item"])), key=lambda a: a.host
    )


def _parse_host_override(host: dict[str, Any]) -> entities.HostOverride:
    return entities.HostOverride(
        host=host["host"],
        domain=host["domain"],
        ip=host["ip"],
        description=host["descr"],
        aliases=__parse_host_override_aliases(host["aliases"]),  # type: ignore
    )


# pylint: disable=too-few-public-methods
class UnboundApi(api.UnboundApi):
    def __init__(
        self,
        proxy: xc.ServerProxy,
        timeout_in_milliseconds: int = DEFAULT_TIMEOUT_IN_MILLISECONDS,
    ):
        self.__proxy = proxy
        self.__timeout_in_seconds = timeout_in_milliseconds / 1_000

    def host_overrides(self) -> list[entities.HostOverride]:
        hosts_r: str = self.__proxy.pfsense.exec_php(
            "$toreturn = json_encode(config_get_path('unbound/hosts', []));",
            self.__timeout_in_seconds,
        )  # type: ignore

        hosts = json.loads(hosts_r)

        return sorted(list(map(_parse_host_override, hosts)), key=lambda h: h.host)
