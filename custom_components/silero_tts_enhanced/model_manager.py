# custom_components/silero_tts_enhanced/model_manager.py
"""Module for fetching and parsing Silero models configuration."""

import logging
import aiohttp
import yaml
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import MODELS_YAML_URL

_LOGGER = logging.getLogger(__name__)


async def async_fetch_silero_models(hass: HomeAssistant) -> dict:
    """Fetch and parse the Silero models.yml file dynamically."""
    session = async_get_clientsession(hass)
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with session.get(MODELS_YAML_URL, timeout=timeout) as response:
            response.raise_for_status()
            text = await response.text()
            data = yaml.safe_load(text)
            
            if isinstance(data, dict) and "tts_models" in data:
                _LOGGER.info("Successfully fetched and parsed Silero models configuration")
                return data["tts_models"]
            
            _LOGGER.warning("Unexpected YAML structure: 'tts_models' key not found")
            return {}
            
    except aiohttp.ClientError as err:
        _LOGGER.error("Network error while fetching Silero models: %s", err)
    except yaml.YAMLError as err:
        _LOGGER.error("Failed to parse Silero models YAML: %s", err)
    except Exception as err:
        _LOGGER.error("Unexpected error fetching Silero models: %s", err)
        
    return {}
