import html
import re
import socket


def ip(value: str) -> bool:
    try:
        socket.inet_aton(value)
        return True
    except socket.error:
        return False


# only checks for valid characters, not for valid host
def host(value: str) -> bool:
    return re.match(r"^[a-zA-Z0-9-_]+$", value) is not None


# only checks for valid characters, not for valid domain
def domain(
    value: str,
) -> bool:
    return re.match(r"^[a-zA-Z0-9-.]+$", value) is not None


def positive(value: int) -> bool:
    return value >= 0
