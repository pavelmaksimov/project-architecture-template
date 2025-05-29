from typing import Protocol


class IGenerateGateway(Protocol):
    def generate(self, messages: list[str]) -> str: ...
