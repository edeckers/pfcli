from pfcli.consts import SUPPORTED_OUTPUT_FORMATS
from pfcli.domain.firmware.entities import Firmware
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import AggregatePrinter
from pfcli.domain.unbound.entities import HostOverride
from pfcli.plugins.printers import json, text

__printers = {
    "json": AggregatePrinter(
        {
            Firmware: json.FirmwarePrinter(),
            HostOverride: json.HostOverridePrinter(),
            HostOverride.Alias: json.HostOverrideAliasPrinter(),
            Info: json.InfoPrinter(),
        },
        json.JsonListPrinter.print,
    ),
    "text": AggregatePrinter(
        {
            Firmware: text.FirmwarePrinter(),
            HostOverride: text.HostOverridePrinter(),
            HostOverride.Alias: text.HostOverrideAliasPrinter(),
            Info: text.InfoPrinter(),
        },
        text.TextListPrinter("\n\n").print,
    ),
}


def create_printer(output_format: str) -> AggregatePrinter:
    maybe_printer = __printers.get(output_format)
    if maybe_printer:
        return maybe_printer

    raise ValueError(
        f"Unsupported output format '{output_format}', expected one of {SUPPORTED_OUTPUT_FORMATS}"
    )
