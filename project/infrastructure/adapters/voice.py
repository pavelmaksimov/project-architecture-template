import asyncio
import io
from io import BytesIO

import openai
from llm_common.prometheus import action_tracking_decorator
from pydub import AudioSegment

from project.utils.retry import retry_unless_exception

exclude_exceptions_from_retry = (
    openai.BadRequestError,
    openai.RateLimitError,
    openai.AuthenticationError,
    openai.PermissionDeniedError,
    openai.NotFoundError,
    openai.ConflictError,
    openai.UnprocessableEntityError,
)


class VoiceAdapter:
    def __init__(
        self,
        client: openai.AsyncClient,
        stt_model: str = "gpt-4o-mini-transcribe",
        tts_model: str = "gpt-4o-mini-tts",
    ):
        self.client = client
        self.stt_model = stt_model
        self.tts_model = tts_model

    def convert_ogg_to_wav_bytes(self, ogg_data: bytes) -> BytesIO:
        """
        Конвертирует OGG аудио из bytes в WAV (mono, 16kHz, PCM16) и возвращает BytesIO.
        """
        audio = AudioSegment.from_ogg(BytesIO(ogg_data))
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # Экспортируем в WAV формат в памяти.
        wav_buffer = BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        wav_buffer.name = "audio.wav"

        return wav_buffer

    async def transcriptions(self, wav_buffer, lang: str = "ru"):
        resp = await self.client.audio.transcriptions.create(
            model=self.stt_model,
            file=wav_buffer,
            language=lang,
            response_format="text",
        )

        return resp if isinstance(resp, str) else getattr(resp, "text", str(resp))

    @retry_unless_exception(exclude_exceptions_from_retry, max_attempts=6, backoff=3)  # di: skip
    @action_tracking_decorator("voice_to_text")
    async def voice_to_text(self, voice: bytes | bytearray) -> str:
        """
        Конвертирует входной .ogg в WAV (mono, 16kHz, PCM16) и отправляет в транскрибацию.

        Для телеграм используйте скачивание в байты

        ogg_data = await voice_file.download_as_bytearray()
        await voice_to_text(ogg_data)
        """
        wav_buffer = await asyncio.to_thread(self.convert_ogg_to_wav_bytes, bytes(voice))
        return await self.transcriptions(wav_buffer)

    @retry_unless_exception(exclude_exceptions_from_retry, max_attempts=6, backoff=3)  # di: skip
    @action_tracking_decorator("voice_from_text")
    async def text_to_voice(
        self,
        text: str,
        instructions: str,
        voice: str = "alloy",
        **kwargs,
    ) -> io.BytesIO:
        response = await self.client.audio.speech.create(
            model=self.tts_model,
            voice=voice,
            input=text,
            instructions=instructions,
            **kwargs,
        )
        file = io.BytesIO(response.content)
        file.name = "voice.mp3"
        file.seek(0)

        return file
