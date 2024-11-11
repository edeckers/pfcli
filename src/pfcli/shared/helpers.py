from typing import Any, TypeVar

from pfcli.consts import DEFAULT_INDENT

ValueT = TypeVar("ValueT", str, float, int)


def v(path: str, data: dict[str, Any], t: type[ValueT]) -> ValueT | None:
    parts = path.split(".")

    r = data
    for part in parts:
        if part not in r:
            return None

        r = r[part]

    return t(r)  # type: ignore


def indent(s: str, prefix: str | None = None) -> str:
    p = prefix or DEFAULT_INDENT

    return "\n".join([f"{p}{line}" for line in s.split("\n")])
