from dataclasses import replace
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
EXIT_INDEX_OUT_OF_BOUNDS = 101


def _sort_aliases(aliases: list[HostOverride.Alias]) -> list[HostOverride]:
    return sorted(aliases, key=lambda a: f"{a.host}{a.domain}")


def _sort_by_hostname(host_overrides: list[HostOverride]) -> list[HostOverride]:
    return sorted(
        [
            replace(host_override, aliases=_sort_aliases(host_overrides))
            for host_override in host_overrides
        ],
        key=lambda o: f"{o.host}{o.domain}",
    )


# pylint: disable=too-few-public-methods
class UboundHandler:
    def __init__(self, backend: Backend) -> None:
        self.__backend = backend

    def host_overrides(self, sort_by_hostname: bool = False) -> list[HostOverride]:
        unsorted_host_overrides = self.__backend.unbound.host_overrides.list()

        return (
            _sort_by_hostname(unsorted_host_overrides)
            if sort_by_hostname
            else unsorted_host_overrides
        )

    def host_override_add(  # pylint: disable=too-many-arguments
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

    def host_override_update(  # pylint: disable=too-many-arguments
        self,
        index: int,
        domain: str,
        host: str,
        ip: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> tuple[None, int]:
        if not validate.domain(domain):
            print(f"Invalid domain name '{domain}'")
            return None, EXIT_SANITIZE_FAILED

        if not validate.host(host):
            print(f"Invalid host name '{host}'")
            return None, EXIT_SANITIZE_FAILED

        all_host_overrides = self.__backend.unbound.host_overrides.list()
        if not 0 <= index < len(all_host_overrides):
            return [None, EXIT_INDEX_OUT_OF_BOUNDS]

        host_override = all_host_overrides[index]

        self.__backend.unbound.host_overrides.update(
            index,
            replace(
                host_override,
                domain=domain,
                host=host,
                ip=ip,
                description=sanitize.escape(description or ""),
            ),
            sanitize.escape(reason or ""),
        )

        return None, EXIT_OK

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

    def host_override_alias_list(
        self,
        host_override_index: int,
        sort_by_hostname: bool = False,
    ) -> tuple[list[HostOverride.Alias], int]:
        all_host_overrides = self.__backend.unbound.host_overrides.list()
        if not 0 <= host_override_index < len(all_host_overrides):
            return [None, EXIT_INDEX_OUT_OF_BOUNDS]

        host_override = all_host_overrides[host_override_index]

        return (
            _sort_aliases(host_override.aliases)
            if sort_by_hostname
            else host_override.aliases
        ), EXIT_OK

    def host_override_alias_add(  # pylint: disable=too-many-arguments
        self,
        host_override_index: int,
        domain: str,
        host: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> tuple[None, int]:
        if not validate.domain(domain):
            print(f"Invalid domain name '{domain}'")
            return None, EXIT_SANITIZE_FAILED

        if not validate.host(host):
            print(f"Invalid host name '{host}'")
            return None, EXIT_SANITIZE_FAILED

        all_host_overrides = self.__backend.unbound.host_overrides.list()
        if not 0 <= host_override_index < len(all_host_overrides):
            return [None, EXIT_INDEX_OUT_OF_BOUNDS]

        host_override = all_host_overrides[host_override_index]

        self.__backend.unbound.host_overrides.update(
            host_override_index,
            replace(
                host_override,
                aliases=_sort_aliases(
                    host_override.aliases
                    + [
                        HostOverride.Alias(
                            domain=domain,
                            host=host,
                            description=sanitize.escape(description or ""),
                        )
                    ],
                ),
            ),
            sanitize.escape(reason or ""),
        )

        return None, EXIT_OK

    def host_override_alias_delete(
        self,
        host_override_index: int,
        host_override_alias_index: int,
        reason: str | None = None,
    ) -> tuple[None, int]:
        all_host_overrides = self.__backend.unbound.host_overrides.list()
        if not 0 <= host_override_index < len(all_host_overrides):
            return [None, EXIT_INDEX_OUT_OF_BOUNDS]

        host_override = all_host_overrides[host_override_index]

        if not 0 <= host_override_alias_index < len(host_override.aliases):
            return [None, EXIT_INDEX_OUT_OF_BOUNDS]

        new_host_override = replace(
            host_override,
            aliases=[
                alias
                for i, alias in enumerate(host_override.aliases)
                if i != host_override_alias_index
            ],
        )

        self.__backend.unbound.host_overrides.update(
            host_override_index, new_host_override, reason
        )

        return None, EXIT_OK


def create_cli(backend: Backend, printers: dict[str, AggregatePrinter]) -> click.Group:
    __unbound_handler = UboundHandler(backend)

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
        host_overrides = __unbound_handler.host_overrides(print_sorted)

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
        _, code = __unbound_handler.host_override_add(
            domain, host, ip, description, reason
        )

        sys.exit(code)

    @unbound.command("update-host-override")
    @click.option(
        "--host-index",
        "host_index",
        help="Index of the host in the *unsorted* host list",
        type=int,
        required=True,
    )
    @click.option("--domain", help="Domain name", required=True)
    @click.option("--host", help="Host name", required=True)
    @click.option("--ip", help="Target IP address", required=True)
    @click.option("--description", help="Description for the entry", required=False)
    @click.option(
        "--reason", help="Description for the configuration log", required=False
    )
    def unbound_host_override_update(  # pylint: disable=too-many-arguments
        host_index: int,
        domain: str,
        host: str,
        ip: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> None:
        _, code = __unbound_handler.host_override_update(
            host_index, domain, host, ip, description, reason
        )

        sys.exit(code)

    @unbound.command("delete-host-override")
    @click.option(
        "--host-index",
        "host_index",
        help="Index of the host in the *unsorted* host list",
        type=int,
        required=True,
    )
    @click.option(
        "--reason", help="Description for the configuration log", required=False
    )
    def unbound_host_override_delete(
        host_index: int,
        reason: str | None = None,
    ) -> None:
        _, code = __unbound_handler.host_override_delete(host_index, reason)

        sys.exit(code)

    @unbound.command("add-host-override-alias")
    @click.option(
        "--host-index",
        "host_index",
        help="Index of the host in the *unsorted* host list",
        type=int,
        required=True,
    )
    @click.option("--domain", help="Domain name", required=True)
    @click.option("--host", help="Host name", required=True)
    @click.option("--description", help="Description for the entry", required=False)
    @click.option(
        "--reason", help="Description for the configuration log", required=False
    )
    def unbound_host_override_alias_add(  # pylint: disable=too-many-arguments
        host_index: int,
        domain: str,
        host: str,
        description: str | None = None,
        reason: str | None = None,
    ) -> None:
        _, code = __unbound_handler.host_override_alias_add(
            host_index, domain, host, description, reason
        )

        sys.exit(code)

    @unbound.command("delete-host-override-alias")
    @click.option(
        "--host-index",
        "host_index",
        help="Index of the host in the *unsorted* host list",
        type=int,
        required=True,
    )
    @click.option(
        "--alias-index",
        "alias_index",
        help="Index of the alias in the *unsorted* alias list",
        type=int,
        required=True,
    )
    @click.option(
        "--reason", help="Description for the configuration log", required=False
    )
    def unbound_host_override_alias_delete(
        host_index: int,
        alias_index: int,
        reason: str | None = None,
    ) -> None:
        _, code = __unbound_handler.host_override_alias_delete(
            host_index, alias_index, reason
        )

        sys.exit(code)

    @unbound.command("list-host-override-aliases")
    @click.option(
        "--host-index",
        "host_index",
        help="Index of the host in the *unsorted* host list",
        type=int,
        required=True,
    )
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
    def unbound_host_override_alias_list(  # pylint: disable=too-many-arguments
        host_index: int,
        output: str,
        print_sorted: bool = False,
    ) -> None:
        host_override_aliases, code = __unbound_handler.host_override_alias_list(
            host_index, print_sorted
        )

        maybe_printer = printers.get(output)
        if maybe_printer:
            print(maybe_printer.print_list(host_override_aliases, HostOverride.Alias))

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

        host_overrides = __unbound_handler.host_overrides(print_sorted)

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
