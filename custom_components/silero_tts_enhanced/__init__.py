# custom_components/silero_tts_enhanced/__init__.py
"""The Silero TTS Enhanced integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN
from .model_manager import async_fetch_silero_models

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["tts"]

# Indicate that this integration only supports config flow setup
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Silero TTS Enhanced integration."""
    hass.data.setdefault(DOMAIN, {})
    
    # Fetch models asynchronously in the background to avoid blocking startup
    hass.async_create_task(_load_models_background(hass))
    
    return True


async def _load_models_background(hass: HomeAssistant) -> None:
    """Background task to load and cache Silero models."""
    models = await async_fetch_silero_models(hass)
    hass.data[DOMAIN]["models"] = models
    if models:
        _LOGGER.info("Loaded %d language configurations for Silero TTS", len(models))
    else:
        _LOGGER.warning("Using fallback model lists due to fetch failure")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Silero TTS Enhanced from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
