from pfcli.bootstrap.backend_factory import create_backend
from pfcli.bootstrap.cli_factory import create_cli
from pfcli.bootstrap.printer_factory import create_printer

backend = create_backend("xmlrpc")

printer_json = create_printer("json")
printer_text = create_printer("text")
printers = {"json": printer_json, "text": printer_text}

cli = create_cli(backend, printers)


if __name__ == "__main__":
    cli()
