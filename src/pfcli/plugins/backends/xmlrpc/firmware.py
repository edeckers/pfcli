import xmlrpc.client as xc  # nosec # B411 - patch applied below, but bandit does not detect it
from typing import Any

import defusedxml.xmlrpc as dxmlrpc

from pfcli.consts import DEFAULT_TIMEOUT_IN_SECONDS
from pfcli.domain.firmware import api, entities
from pfcli.shared.helpers import v

dxmlrpc.monkey_patch()  # Fix for [B411:blacklist] xmlrpc.client XML vulnerability


# pylint: disable=too-few-public-methods
class FirmwareApi(api.FirmwareApi):
    def __init__(
        self,
        proxy: xc.ServerProxy,
        timeout_in_seconds: int = DEFAULT_TIMEOUT_IN_SECONDS,
    ):
        self.__proxy = proxy
        self.__timeout_in_seconds = timeout_in_seconds

    def version(
        self,
    ) -> entities.Firmware:
        r: dict[str, Any] = self.__proxy.pfsense.host_firmware_version(
            "dummy", self.__timeout_in_seconds
        )  # type: ignore

        return entities.Firmware(
            version=v("firmware.version", r, str) or "",
            config=entities.Firmware.Config(v("config_version", r, str) or ""),
            kernel=entities.Firmware.Kernel(v("kernel.version", r, str) or ""),
            platform=v("platform", r, str) or "",
        )
