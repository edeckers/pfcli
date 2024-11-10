import xmlrpc.client as xc
from dataclasses import dataclass

from pfcli.domain.firmware.api import FirmwareApi
from pfcli.consts import SUPPORTED_BACKENDS
from pfcli.plugins.backends.xmlrpc.unbound import UnboundApi
import pfcli.plugins.backends.xmlrpc.unbound as xu
import pfcli.plugins.backends.xmlrpc.firmware as xv
from pfcli.config import (
    APPLICATION_PFSENSE_PASSWORD,
    APPLICATION_PFSENSE_HOSTNAME,
    APPLICATION_PFSENSE_USERNAME,
)


@dataclass(frozen=True)
class Backend:
    unbound: UnboundApi
    firmware: FirmwareApi


def create_backend(backend_type: str) -> Backend:
    if backend_type not in SUPPORTED_BACKENDS:
        raise ValueError(
            # pylint: disable=line-too-long
            f"Invalid backend type '{backend_type}', expected one of {",".join(SUPPORTED_BACKENDS)}"
        )

    proxy = xc.ServerProxy(
        # pylint: disable=line-too-long
        f"https://{APPLICATION_PFSENSE_USERNAME}:{APPLICATION_PFSENSE_PASSWORD}@{APPLICATION_PFSENSE_HOSTNAME}/xmlrpc.php"
    )

    return Backend(unbound=xu.UnboundApi(proxy), firmware=xv.FirmwareApi(proxy))
