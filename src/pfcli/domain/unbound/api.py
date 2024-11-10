from __future__ import annotations
from abc import ABC, abstractmethod

from pfcli.domain.unbound.entities import HostOverride


# pylint: disable=too-few-public-methods
class UnboundApi(ABC):
    class HostOverridesApi(ABC):
        @abstractmethod
        def list(self) -> list[HostOverride]:
            raise NotImplementedError(
                "host_overrides() must be implemented in a subclass"
            )

        @abstractmethod
        def add(
            self, override: HostOverride, message_reason: str | None = None
        ) -> None:
            raise NotImplementedError(
                "host_override_add() must be implemented in a subclass"
            )

        @abstractmethod
        def delete(self, index: int, message_reason: str | None = None) -> None:
            raise NotImplementedError(
                "host_override_delete() must be implemented in a subclass"
            )

    @property
    @abstractmethod
    def host_overrides(self) -> UnboundApi.HostOverridesApi:
        raise NotImplementedError("host_overrides() must be implemented in a subclass")
