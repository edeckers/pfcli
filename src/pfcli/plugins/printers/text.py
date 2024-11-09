from typing import Any
from pfcli.domain.firmware.entities import Versioned
from pfcli.domain.firmware.firmware import Firmware
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import Printer
from pfcli.domain.unbound.unbound import HostOverride
from pfcli.plugins.backends.xmlrpc.helpers import indent


# pylint: disable=too-few-public-methods
class VersionedPrinter(Printer[Versioned]):
    def print(self, printable: Versioned) -> str:
        return f"version: {printable.version}"


# pylint: disable=too-few-public-methods
class FirmwareConfigPrinter(Printer[Firmware.Config]):
    def print(self, printable: Firmware.Config) -> str:
        return VersionedPrinter().print(printable)


FirmwareConfigPrinter = VersionedPrinter
FirmwareKernelPrinter = VersionedPrinter


# pylint: disable=too-few-public-methods
class FirmwarePrinter(Printer[Firmware]):
    __config_printer = FirmwareConfigPrinter()
    __kernel_printer = FirmwareKernelPrinter()

    def print(self, printable: Firmware) -> str:
        return "\n".join(
            [
                "config:",
                indent(self.__config_printer.print(printable.config)),
                "",
                "kernel:",
                indent(self.__kernel_printer.print(printable.kernel)),
                "",
                f"platform: {printable.platform}",
                "",
                f"version: {printable.version}",
            ]
        )


class HostOverrideAliasPrinter(Printer[HostOverride.Alias]):
    def print(self, printable: HostOverride.Alias) -> str:
        fields = f"{printable.host}.{printable.domain}"

        if not printable.description:
            return fields

        return f"{fields} - {printable.description}"


class HostOverridePrinter(Printer[HostOverride]):
    __alias_printer = HostOverrideAliasPrinter()

    def print(self, printable: HostOverride) -> str:
        fields = f"{printable.host}.{printable.domain} {printable.ip}"

        head = (
            f"{fields} - {printable.description}" if printable.description else fields
        )

        aliases = "\n".join(map(self.__alias_printer.print, printable.aliases))

        return head if not aliases else f"{head}\n\n{indent(aliases)}"


class InfoPrinter(Printer[Info]):
    def print(self, printable: Info) -> str:
        firmware_printer = FirmwarePrinter()
        host_override_printer = HostOverridePrinter()

        return "\n".join(
            [
                "FIRMWARE",
                "",
                firmware_printer.print(printable.firmware),
                "",
                "HOST OVERRIDES",
                "",
                "\n\n".join(map(host_override_printer.print, printable.host_overrides)),
            ]
        )
