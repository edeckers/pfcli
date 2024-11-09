from dataclasses import asdict, dataclass
import json
from pfcli.domain.firmware.firmware import Firmware
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import Printer
from pfcli.domain.unbound.unbound import HostOverride


# pylint: disable=too-few-public-methods
class FirmwarePrinter(Printer[Firmware]):
    def print(self, printable: Firmware) -> str:
        return json.dumps(
            {
                "config": asdict(printable.config),
                "kernel": asdict(printable.kernel),
                "platform": printable.platform,
                "version": printable.version,
            }
        )


class HostOverrideAliasPrinter(Printer[HostOverride.Alias]):
    def print(self, printable: HostOverride.Alias) -> str:
        return json.dumps(asdict(printable))


class HostOverridePrinter(Printer[HostOverride]):
    def print(self, printable: HostOverride) -> str:
        return json.dumps(asdict(printable))


class InfoPrinter(Printer[Info]):
    def print(self, printable: Info) -> str:
        return json.dumps(asdict(printable))
