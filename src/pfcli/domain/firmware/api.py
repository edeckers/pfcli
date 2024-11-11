from __future__ import annotations

from abc import ABC, abstractmethod

from pfcli.domain.firmware.entities import Firmware


# pylint: disable=too-few-public-methods
class FirmwareApi(ABC):
    @abstractmethod
    def version(self) -> Firmware:
        raise NotImplementedError("version() must be implemented in a subclass")
