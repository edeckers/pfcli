# pylint: disable=too-few-public-methods
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

DataT = TypeVar("DataT")


class Printer(ABC, Generic[DataT]):
    @abstractmethod
    def print(self, printable: DataT) -> str:
        raise NotImplementedError("print() must be implemented in a subclass")


class AggregatePrinter:
    def __init__(self, printers: dict[type, Printer[Any]]):
        self.__printers = printers

    def print(self, printable: DataT) -> str:
        if type(printable) not in self.__printers:
            raise ValueError(f"Unsupported type {type(printable)}")

        printer = self.__printers[type(printable)]

        return printer.print(printable)
