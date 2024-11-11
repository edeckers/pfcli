import sys

import click

import pfcli.shared.sanitizers as sanitize
import pfcli.shared.validators as validate
from pfcli.bootstrap.backend_factory import Backend
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import AggregatePrinter
from pfcli.domain.unbound.entities import HostOverride

EXIT_OK = 0
EXIT_SANITIZE_FAILED = 100


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
        unsorted_host_overrides = self.__backend.unbound.host_overrides.list()

        return (
            UboundHandler.__sort_by_hostname(unsorted_host_overrides)
            if sort_by_hostname
            else unsorted_host_overrides
        )

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def host_override_add(
        self,
        domain: str,
        host: str,
        ip: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> tuple[None, int]:
        if not validate.ip(ip):
            print(f"Invalid IP address '{ip}'")
            return None, EXIT_SANITIZE_FAILED

        if not validate.domain(domain):
            print(f"Invalid domain name '{domain}'")
            return None, EXIT_SANITIZE_FAILED

        if not validate.host(host):
            print(f"Invalid host name '{host}'")
            return None, EXIT_SANITIZE_FAILED

        self.__backend.unbound.host_overrides.add(
            HostOverride(
                domain=domain,
                host=host,
                ip=ip,
                description=sanitize.escape(description or ""),
                aliases=[],
            ),
            sanitize.escape(reason or ""),
        )

        return None, EXIT_OK

    # pylint: disable=too-many-arguments
    def host_override_delete(
        self,
        index: int,
        reason: str | None = None,
    ) -> tuple[None, int]:
        if not validate.positive(index):
            print(f"Invalid index '{index}'")
            return None, EXIT_SANITIZE_FAILED

        self.__backend.unbound.host_overrides.delete(
            index,
            sanitize.escape(reason or ""),
        )

        return None, EXIT_OK


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

    @unbound.command("add-host-override")
    @click.option("--domain", help="Domain name", required=True)
    @click.option("--host", help="Host name", required=True)
    @click.option("--ip", help="Target IP address", required=True)
    @click.option("--description", help="Description for the entry", required=False)
    @click.option(
        "--reason", help="Description for the configuration log", required=False
    )
    def unbound_host_override_add(
        domain: str,
        host: str,
        ip: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> None:
        _, code = __ubound_handler.host_override_add(
            domain, host, ip, description, reason
        )

        sys.exit(code)

    @unbound.command("delete-host-override")
    @click.option(
        "--index",
        help="Index of the host in the *unsorted* host list",
        type=int,
        required=True,
    )
    @click.option(
        "--reason", help="Description for the configuration log", required=False
    )
    def unbound_host_override_delete(
        index: int,
        reason: str | None = None,
    ) -> None:
        _, code = __ubound_handler.host_override_delete(index, reason)

        sys.exit(code)

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
