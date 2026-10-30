# custom_components/silero_tts_enhanced/tts.py
"""Text-to-Speech platform for Silero TTS Enhanced."""

import logging
import aiohttp
from homeassistant.components.tts import TextToSpeechEntity, ATTR_VOICE
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import Any

from .const import DOMAIN, DEFAULT_SAMPLE_RATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities
) -> None:
    """Set up the Silero TTS platform."""
    async_add_entities([SileroTTSAPIEntity(hass, config_entry)])


class SileroTTSAPIEntity(TextToSpeechEntity):
    """Representation of a Silero TTS entity."""

    _attr_name = "Silero TTS Enhanced"
    _attr_has_entity_name = False

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the TTS entity."""
        self.hass = hass
        
        # Prioritize options over initial data for runtime configuration
        data = config_entry.options if config_entry.options else config_entry.data
        
        self._host = data.get("host", "").rstrip("/")
        self._lang = data.get("language", "ru")
        self._model_id = data.get("model_id", "v5_ru")
        self._sample_rate = data.get("sample_rate", DEFAULT_SAMPLE_RATE)
        self._speaker = data.get("speaker", "aidar")
        self._put_accent = data.get("put_accent", True)
        self._put_yo = data.get("put_yo", True)
        
        self._attr_unique_id = f"{config_entry.entry_id}_tts"

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        # Fallback list; dynamic fetching is handled in config flow
        return ["ru", "en", "de", "es", "fr", "tt", "uz", "ua", "multi"]

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return self._lang

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return [ATTR_VOICE, "model_id", "put_accent", "put_yo", "sample_rate"]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return a dict of default options."""
        return {
            ATTR_VOICE: self._speaker,
            "model_id": self._model_id,
            "put_accent": self._put_accent,
            "put_yo": self._put_yo,
            "sample_rate": self._sample_rate,
        }

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict
    ) -> tuple[str | None, bytes | None]:
        """Generate TTS audio asynchronously."""
        payload = {
            "text": message, 
            "language": language,
            "voice": options.get(ATTR_VOICE, self._speaker),
            "model_id": options.get("model_id", self._model_id),
            "sample_rate": options.get("sample_rate", self._sample_rate),
            "put_accent": options.get("put_accent", self._put_accent),
            "put_yo": options.get("put_yo", self._put_yo),
        }
        
        session = async_get_clientsession(self.hass)
        try:
            timeout = aiohttp.ClientTimeout(total=60)
            url = f"{self._host}/tts"
            
            async with session.post(url, json=payload, timeout=timeout) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    if not audio_data:
                        _LOGGER.warning("Received empty audio data from Silero TTS")
                        return None, None
                    return "wav", audio_data
                else:
                    error_text = await response.text()
                    _LOGGER.error("Silero TTS API error (%s): %s", response.status, error_text)
                    
        except TimeoutError:
            _LOGGER.error("Timeout while connecting to Silero TTS at %s", self._host)
        except aiohttp.ClientError as err:
            _LOGGER.error("Network connection error to Silero TTS: %s", err)
        except Exception as err:
            _LOGGER.error("Unexpected error during TTS generation: %s", err)
            
        return None, None
