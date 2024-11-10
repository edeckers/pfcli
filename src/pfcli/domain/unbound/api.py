from __future__ import annotations
from abc import ABC, abstractmethod

from pfcli.domain.unbound.entities import HostOverride


# pylint: disable=too-few-public-methods
class UnboundApi(ABC):
    @abstractmethod
    def host_overrides(self) -> list[HostOverride]:
        raise NotImplementedError("host_overrides() must be implemented in a subclass")

    @abstractmethod
    def host_override_add(
        self, override: HostOverride, message_reason: str | None = None
    ) -> None:
        raise NotImplementedError(
            "host_override_add() must be implemented in a subclass"
        )
