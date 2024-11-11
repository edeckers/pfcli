from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HostOverride:
    @dataclass(frozen=True)
    class Alias:
        host: str
        domain: str
        description: str | None = None

        def __str__(self) -> str:
            fields = f"{self.host}.{self.domain}"

            if not self.description:
                return fields

            return f"{fields} - {self.description}"

    domain: str
    host: str
    ip: str
    aliases: list[HostOverride.Alias]
    description: str | None = None
