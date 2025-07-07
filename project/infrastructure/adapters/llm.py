import typing as t

from project.domains.chat.interfaces import IGenerateGateway


class LLMClient(IGenerateGateway):
    def generate(self, messages: t.Iterable[str]) -> str:  # noqa: ARG002
        fantasy = ""

        return fantasy

    def voice_to_text(self, audio_file_path) -> str:  # noqa: ARG002
        fantasy = ""

        return fantasy
