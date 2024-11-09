import click

from pfcli.bootstrap.backend_factory import Backend
from pfcli.domain.info import Info
from pfcli.domain.printers.printers import AggregatePrinter


def create_cli(backend: Backend, printers: dict[str, AggregatePrinter]) -> click.Group:
    @click.group()
    def cli() -> click.Group:  # type: ignore
        pass

    @click.command("info")
    @click.option(
        "--output",
        default="text",
        help=f'The output format, one of {",".join(printers.keys())}',
    )
    def info(output: str) -> None:
        version = backend.firmware.version()
        host_overrides = backend.unbound.host_overrides()

        maybe_printer = printers.get(output)

        if not maybe_printer:
            print(
                f"Unsupported output format '{output}', expected one of {','.join(printers.keys())}"
            )
            return

        print(maybe_printer.print(Info(version, host_overrides)))

    cli.add_command(info)

    return cli
