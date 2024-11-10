# pylint: disable=too-few-public-methods
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

DataT = TypeVar("DataT")


class Printer(ABC, Generic[DataT]):
    @abstractmethod
    def print(self, printable: DataT) -> str:
        raise NotImplementedError("print() must be implemented in a subclass")


class AggregatePrinter:
    def __init__(
        self,
        printers: dict[type, Printer[Any]],
        list_printer: Callable[[Printer[Any], list[Any]], str],
    ):
        self.__printers = printers
        self.__list_printer = list_printer

    def print(self, printable: DataT) -> str:
        if type(printable) not in self.__printers:
            raise ValueError(f"Unsupported type {type(printable)}")

        printer = self.__printers[type(printable)]

        return printer.print(printable)

    def print_list(self, printable: list[DataT], t: type[DataT]) -> str:
        if t not in self.__printers:
            raise ValueError(f"Unsupported type {type(printable)}")

        printer = self.__printers[t]

        return self.__list_printer(printer, printable)
