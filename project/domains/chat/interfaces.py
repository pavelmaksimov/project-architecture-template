from typing import Protocol, Iterable


class IGenerateGateway(Protocol):
    def generate(self, messages: Iterable[str]) -> str: ...
