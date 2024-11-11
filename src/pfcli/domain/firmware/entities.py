from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Versioned:
    version: str


@dataclass(frozen=True)
class Firmware(Versioned):
    @dataclass(frozen=True)
    class Config(Versioned):
        pass

    @dataclass(frozen=True)
    class Kernel(Versioned):
        pass

    config: Firmware.Config
    kernel: Firmware.Kernel
    platform: str
