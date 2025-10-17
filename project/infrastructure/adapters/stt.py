import asyncio
from io import BytesIO

from llm_common.prometheus import action_tracking_decorator
import openai
from pydub import AudioSegment


class STTAdapter:
    def __init__(self, client: openai.AsyncClient, model: str = "gpt-4o-mini-transcribe", lang: str = "ru"):
        self.client = client
        self.model = model
        self.lang = lang

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

    async def transcriptions(self, wav_buffer):
        resp = await self.client.audio.transcriptions.create(
            model=self.model,  # TODO: move settings
            file=wav_buffer,
            language=self.lang,
            response_format="text",
        )

        return resp if isinstance(resp, str) else getattr(resp, "text", str(resp))

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
