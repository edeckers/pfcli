import xmlrpc.client as xc  # nosec # B411 - patch applied below, but bandit does not detect it

import defusedxml.xmlrpc as dxmlrpc

dxmlrpc.monkey_patch()  # Fix for [B411:blacklist] xmlrpc.client XML vulnerability


# pylint: disable=too-few-public-methods
class CommandRunner:
    def __init__(self, proxy: xc.ServerProxy, timeout_in_seconds: float):
        self.__timeout_in_seconds = timeout_in_seconds
        self.__proxy = proxy

    def exec(self, commands: list[str]) -> str:
        return self.__proxy.pfsense.exec_php(
            "\n".join(commands), self.__timeout_in_seconds
        )  # type: ignore
