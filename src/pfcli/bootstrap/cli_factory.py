import click

from pfcli.bootstrap.backend_factory import Backend
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import AggregatePrinter
from pfcli.domain.unbound.entities import HostOverride


# pylint: disable=too-few-public-methods
class UboundHandler:
    def __init__(self, backend: Backend) -> None:
        self.__backend = backend

    @staticmethod
    def __sort_aliases(host_overrides: list[HostOverride]) -> list[HostOverride]:
        return [
            HostOverride(
                host=host_override.host,
                domain=host_override.domain,
                ip=host_override.ip,
                description=host_override.description,
                aliases=sorted(host_override.aliases, key=lambda a: a.host),
            )
            for host_override in host_overrides
        ]

    @staticmethod
    def __sort_by_hostname(host_overrides: list[HostOverride]) -> list[HostOverride]:
        return sorted(
            UboundHandler.__sort_aliases(host_overrides), key=lambda o: o.host
        )

    def host_overrides(self, sort_by_hostname: bool = False) -> list[HostOverride]:
        unsorted_host_overrides = self.__backend.unbound.host_overrides()

        return (
            UboundHandler.__sort_by_hostname(unsorted_host_overrides)
            if sort_by_hostname
            else unsorted_host_overrides
        )


def create_cli(backend: Backend, printers: dict[str, AggregatePrinter]) -> click.Group:
    __ubound_handler = UboundHandler(backend)

    @click.group()
    def cli() -> click.Group:  # type: ignore
        pass

    @click.group("firmware")
    def firmware() -> None:
        pass

    @firmware.command("version")
    @click.option(
        "--output",
        default="text",
        help=f'The output format, one of {",".join(printers.keys())}',
    )
    def firmware_version(output: str) -> None:
        version = backend.firmware.version()

        maybe_printer = printers.get(output)
        if maybe_printer:
            print(maybe_printer.print(version))

    @click.group("unbound")
    def unbound() -> None:
        pass

    @unbound.command("list-host-overrides")
    @click.option(
        "--output",
        default="text",
        help=f'The output format, one of {",".join(printers.keys())}',
    )
    @click.option(
        "--sorted",
        "print_sorted",
        help="Sort list of host overrides by host name?",
        is_flag=True,
    )
    def unbound_host_overrides(output: str, print_sorted: bool = False) -> None:
        host_overrides = __ubound_handler.host_overrides(print_sorted)

        maybe_printer = printers.get(output)
        if maybe_printer:
            print(maybe_printer.print_list(host_overrides, HostOverride))

    @click.command("info")
    @click.option(
        "--output",
        default="text",
        help=f'The output format, one of {",".join(printers.keys())}',
    )
    @click.option(
        "--sorted",
        "print_sorted",
        help="Sort list of host overrides by host name?",
        is_flag=True,
    )
    def info(output: str, print_sorted: bool = False) -> None:
        version = backend.firmware.version()

        host_overrides = __ubound_handler.host_overrides(print_sorted)

        maybe_printer = printers.get(output)

        if not maybe_printer:
            print(
                f"Unsupported output format '{output}', expected one of {','.join(printers.keys())}"
            )
            return

        print(maybe_printer.print(Info(version, host_overrides)))

    cli.add_command(firmware)
    cli.add_command(unbound)
    cli.add_command(info)

    return cli
