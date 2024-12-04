from __future__ import annotations

from abc import ABC, abstractmethod

from pfcli.domain.unbound.entities import HostOverride


# pylint: disable=too-few-public-methods
class UnboundApi(ABC):
    class HostOverridesApi(ABC):
        @abstractmethod
        def list(self) -> list[HostOverride]:
            raise NotImplementedError("list() must be implemented in a subclass")

        @abstractmethod
        def add(
            self, override: HostOverride, message_reason: str | None = None
        ) -> None:
            raise NotImplementedError("add() must be implemented in a subclass")

        @abstractmethod
        def update(
            self, index: int, override: HostOverride, message_reason: str | None = None
        ) -> None:
            raise NotImplementedError("update() must be implemented in a subclass")

        @abstractmethod
        def delete(self, index: int, message_reason: str | None = None) -> None:
            raise NotImplementedError("delete() must be implemented in a subclass")

    @property
    @abstractmethod
    def host_overrides(self) -> UnboundApi.HostOverridesApi:
        raise NotImplementedError("host_overrides() must be implemented in a subclass")
