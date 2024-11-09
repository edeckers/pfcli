from typing import Any
import xmlrpc.client as xc

from pfcli.consts import DEFAULT_TIMEOUT_IN_MILLISECONDS
import pfcli.domain.firmware.entities as entities
import pfcli.domain.firmware.firmware as api
from pfcli.plugins.backends.xmlrpc.helpers import v


# pylint: disable=too-few-public-methods
class FirmwareApi(api.FirmwareApi):
    def __init__(
        self,
        proxy: xc.ServerProxy,
        timeout_in_milliseconds: int = DEFAULT_TIMEOUT_IN_MILLISECONDS,
    ):
        self.__proxy = proxy
        self.__timeout_in_seconds = timeout_in_milliseconds / 1_000

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