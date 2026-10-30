# custom_components/silero_tts_enhanced/config_flow.py
"""Config flow for Silero TTS Enhanced."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.config_entries import OptionsFlowWithReload
from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    DEFAULT_SPEAKER,
    DEFAULT_SAMPLE_RATE,
)

_LOGGER = logging.getLogger(__name__)


class SileroTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Silero TTS Enhanced."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict = {}

    async def async_step_user(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Step 1: Get the host URL."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_language()

        schema = vol.Schema({
            vol.Required("host", default=DEFAULT_HOST): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_language(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Step 2: Select language dynamically."""
        models_data = self.hass.data.get(DOMAIN, {}).get("models", {})
        languages = list(models_data.keys()) if models_data else [DEFAULT_LANGUAGE, "en", "de", "es", "fr"]

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_model()

        schema = vol.Schema({
            vol.Required("language", default=DEFAULT_LANGUAGE): selector.SelectSelector(
                selector.SelectSelectorConfig(options=languages, custom_value=True)
            )
        })
        return self.async_show_form(step_id="language", data_schema=schema)

    async def async_step_model(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Step 3: Select model dynamically based on language."""
        models_data = self.hass.data.get(DOMAIN, {}).get("models", {})
        lang = self._data.get("language", DEFAULT_LANGUAGE)
        
        lang_models = models_data.get(lang, {})
        model_options = [{"value": m, "label": m} for m in lang_models.keys()]
        
        # Fallback if dynamic fetch failed
        if not model_options:
            model_options = [{"value": DEFAULT_MODEL, "label": DEFAULT_MODEL}, {"value": "v3_en", "label": "v3_en"}]

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_voice()

        default_model = list(lang_models.keys())[0] if lang_models else DEFAULT_MODEL
        schema = vol.Schema({
            vol.Required("model_id", default=default_model): selector.SelectSelector(
                selector.SelectSelectorConfig(options=model_options, custom_value=True)
            )
        })
        return self.async_show_form(step_id="model", data_schema=schema)

    async def async_step_voice(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Step 4: Select speaker and sample rate dynamically based on model."""
        models_data = self.hass.data.get(DOMAIN, {}).get("models", {})
        lang = self._data.get("language", DEFAULT_LANGUAGE)
        model_id = self._data.get("model_id", DEFAULT_MODEL)
        
        model_info = models_data.get(lang, {}).get(model_id, {})
        latest_info = model_info.get("latest", {})
        
        # Extract sample rates
        sr = latest_info.get("sample_rate", [8000, 24000, 48000])
        if isinstance(sr, int):
            sr = [sr]
        sr_options = [{"value": str(r), "label": f"{r} Hz"} for r in sr]
        if not sr_options:
            sr_options = [{"value": str(DEFAULT_SAMPLE_RATE), "label": f"{DEFAULT_SAMPLE_RATE} Hz"}]

        # Extract speakers
        speakers_dict = latest_info.get("speakers", {})
        speaker_options = list(speakers_dict.keys()) if speakers_dict else ["aidar", "baya", "kseniya", "xenia", "eugene"]
        
        if user_input is not None:
            self._data.update(user_input)
            self._data["sample_rate"] = int(self._data["sample_rate"])
            self._data.setdefault("put_accent", True)
            self._data.setdefault("put_yo", True)
            
            return self.async_create_entry(
                title=f"Silero TTS ({self._data['language']})", 
                data=self._data
            )

        default_speaker = speaker_options[0] if speaker_options else DEFAULT_SPEAKER
        default_sr = str(sr[0]) if sr else str(DEFAULT_SAMPLE_RATE)
        
        schema = vol.Schema({
            vol.Required("speaker", default=default_speaker): selector.SelectSelector(
                selector.SelectSelectorConfig(options=speaker_options, custom_value=True)
            ),
            vol.Required("sample_rate", default=default_sr): selector.SelectSelector(
                selector.SelectSelectorConfig(options=sr_options, custom_value=True)
            ),
            vol.Required("put_accent", default=True): bool,
            vol.Required("put_yo", default=True): bool,
        })
        return self.async_show_form(step_id="voice", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "SileroTTSOptionsFlowHandler":
        """Get the options flow for this handler."""
        return SileroTTSOptionsFlowHandler()


class SileroTTSOptionsFlowHandler(OptionsFlowWithReload):
    """Handle options flow for Silero TTS Enhanced."""

    async def async_step_init(self, user_input: dict | None = None) -> config_entries.FlowResult:
        """Manage the options."""
        if user_input is not None:
            user_input["sample_rate"] = int(user_input["sample_rate"])
            return self.async_create_entry(title="", data=user_input)

        # Safely merge data and options
        current = {**self.config_entry.data, **self.config_entry.options}
        current["sample_rate"] = str(current.get("sample_rate", DEFAULT_SAMPLE_RATE))
        
        models_data = self.hass.data.get(DOMAIN, {}).get("models", {})
        lang = current.get("language", DEFAULT_LANGUAGE)
        model_id = current.get("model_id", DEFAULT_MODEL)
        
        # Dynamic options for editing
        lang_models = models_data.get(lang, {})
        model_options = [{"value": m, "label": m} for m in lang_models.keys()]
        
        model_info = lang_models.get(model_id, {})
        latest_info = model_info.get("latest", {})
        
        sr = latest_info.get("sample_rate", [8000, 24000, 48000])
        if isinstance(sr, int):
            sr = [sr]
        sr_options = [{"value": str(r), "label": f"{r} Hz"} for r in sr]
        
        speakers_dict = latest_info.get("speakers", {})
        speaker_options = list(speakers_dict.keys()) if speakers_dict else ["aidar", "baya", "kseniya", "xenia", "eugene"]

        schema = vol.Schema({
            vol.Required("host", default=current.get("host", DEFAULT_HOST)): str,
            vol.Required("language", default=current.get("language", DEFAULT_LANGUAGE)): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(models_data.keys()) if models_data else [DEFAULT_LANGUAGE, "en"], custom_value=True)
            ),
            vol.Required("model_id", default=current.get("model_id", DEFAULT_MODEL)): selector.SelectSelector(
                selector.SelectSelectorConfig(options=model_options, custom_value=True)
            ),
            vol.Required("speaker", default=current.get("speaker", DEFAULT_SPEAKER)): selector.SelectSelector(
                selector.SelectSelectorConfig(options=speaker_options, custom_value=True)
            ),
            vol.Required("sample_rate", default=current.get("sample_rate", str(DEFAULT_SAMPLE_RATE))): selector.SelectSelector(
                selector.SelectSelectorConfig(options=sr_options, custom_value=True)
            ),
            vol.Required("put_accent", default=current.get("put_accent", True)): bool,
            vol.Required("put_yo", default=current.get("put_yo", True)): bool,
        })
        
        return self.async_show_form(step_id="init", data_schema=schema)
