import json
from dataclasses import asdict
from typing import Any

from pfcli.domain.firmware.entities import Firmware
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import Printer
from pfcli.domain.unbound.entities import HostOverride


# pylint: disable=too-few-public-methods
class JsonListPrinter:
    @staticmethod
    def print(printer: Printer[Any], printable: list[Any]) -> str:
        items = ",".join(map(printer.print, printable))

        return f"[{items}]"


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
