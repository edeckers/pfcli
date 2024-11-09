from dataclasses import dataclass

from pfcli.domain.firmware.entities import Firmware
from pfcli.domain.unbound.entities import HostOverride


@dataclass(frozen=True)
class Info:
    firmware: Firmware
    host_overrides: list[HostOverride]
