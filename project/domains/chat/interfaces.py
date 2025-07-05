import typing as t


class IGenerateGateway(t.Protocol):
    def generate(self, messages: t.Iterable[str]) -> str: ...
