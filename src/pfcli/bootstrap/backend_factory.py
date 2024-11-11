import xmlrpc.client as xc  # nosec # B411 - patch applied below, but bandit does not detect it
from dataclasses import dataclass

import defusedxml.xmlrpc as dxmlrpc

import pfcli.plugins.backends.xmlrpc.firmware as xv
import pfcli.plugins.backends.xmlrpc.unbound as xu
from pfcli.config import (
    APPLICATION_PFSENSE_HOSTNAME,
    APPLICATION_PFSENSE_PASSWORD,
    APPLICATION_PFSENSE_SCHEME,
    APPLICATION_PFSENSE_USERNAME,
)
from pfcli.consts import SUPPORTED_BACKENDS
from pfcli.domain.firmware.api import FirmwareApi
from pfcli.plugins.backends.xmlrpc.unbound import UnboundApi

dxmlrpc.monkey_patch()  # Fix for [B411:blacklist] xmlrpc.client XML vulnerability


@dataclass(frozen=True)
class Backend:
    unbound: UnboundApi
    firmware: FirmwareApi


def create_backend(backend_type: str) -> Backend:
    if backend_type not in SUPPORTED_BACKENDS:
        supported_backends_str = ",".join(SUPPORTED_BACKENDS)

        raise ValueError(
            # pylint: disable=line-too-long
            f"Invalid backend type '{backend_type}', expected one of {supported_backends_str}"
        )

    proxy = xc.ServerProxy(
        # pylint: disable=line-too-long
        f"{APPLICATION_PFSENSE_SCHEME}://{APPLICATION_PFSENSE_USERNAME}:{APPLICATION_PFSENSE_PASSWORD}@{APPLICATION_PFSENSE_HOSTNAME}/xmlrpc.php"
    )

    return Backend(unbound=xu.UnboundApi(proxy), firmware=xv.FirmwareApi(proxy))
